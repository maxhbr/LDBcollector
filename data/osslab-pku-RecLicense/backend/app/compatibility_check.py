import subprocess
import json
import os
import pandas as pd 
import tqdm
from .parse_dependency import *
import pymongo
from .z3resolver import *
import logging
from .remediator import *   
logging.basicConfig(
    filename=f"./app/logging/backend.log",
    filemode='a',
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
MONGO_HOST = '127.0.0.1'  # docker container
if "RECLIC_MONGO_PORT" in os.environ:
    MONGO_HOST = 'mongodb'

mongo_client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:27017/')
mongo_db = mongo_client['libraries']
mongo_collection = mongo_db['projects']
mongo_pypi =  mongo_client["license"]["package"]

def compatibility_judge(licenseA,licenseB):
    df = pd.read_csv('./app/knowledgebase/compatibility_63.csv', index_col=0)
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

def license_detection_files(file_path,output_path):
    results={}
    pipe = subprocess.Popen(
        ["../scancode-toolkit/scancode","-l" ,"-n","30","--license-score","95","--json", output_path, file_path,"--license-text"],#relative path
        stdout=subprocess.PIPE)
    return_code=pipe.wait()
    with open(output_path,"r") as f:
        res=json.load(f)
        files=res["files"]
        for file in files:
            licenses=file["licenses"]
            if licenses:
                licenses.sort(key=lambda e: - e["score"])
                licenses_spdx=[]
                for license in licenses:
                    if "scancode" not in license["spdx_license_key"]:
                        licenses_spdx.append(license["spdx_license_key"])
                if "LICENSE" in file["path"]:
                    results["LICENSE"]=list(set(licenses_spdx))
                else:
                    results[file["path"]]=list(set(licenses_spdx))

    dep_license, dep_tree, require_dist=get_dependencies_licenses(file_path)
    results.update(dep_license)
    return results, dep_tree, require_dist

def get_direct_dep(require_dist):
    direct_dep = []
    for i in require_dist:
        try:
            req = Requirement(i)
            dep_name = req.name.lower()
            direct_dep.append(dep_name)
        except:
            continue
    return direct_dep

def get_dependencies_licenses(file_path):
    dep_license={}
    dep=traverse(os.path.abspath(file_path))
    dep_tree = None
    require_dist = None
    for lang in dep:
        if lang != "Python" :
            for p in dep[lang]:
                res=None
                if lang =="Java":
                    res=mongo_collection.find_one({"Name":p,"Language":lang})
                elif lang=="JavaScript":
                    res=mongo_collection.find_one({ "$or" : [{"Name":p,"Language":"JavaScript"},{"Name":p,"Language":"TypeScript"} ]})
                if res:
                    if "," in res['Licenses']:
                        dep_license[f"direct_dependency({p})"]=res['Licenses'].split(",")
                    else:
                        dep_license[f"direct_dependency({p})"]=[res['Licenses']]
            
        if lang=="Python":
            require_dist = list(dep['Python'])
            direct_dep = get_direct_dep(require_dist)
            mongo_uri = "mongodb://localhost:27017/"
            dr = Z3DependencyResolver(mongo_uri, file_path.split("/")[-1])
            dep_tree = dr.resolve(require_dist)
            for i in dep_tree:
                pkg = mongo_pypi.find_one({"name": i, "version": dep_tree[i]})
                if pkg:
                    if i in direct_dep:
                        dep_license[f"direct_dependency({i}_{dep_tree[i]})"] = [pkg["license_clean"]]
                    else:
                        dep_license[f"indirect_dependency({i}_{dep_tree[i]})"] = [pkg["license_clean"]]

    return dep_license , dep_tree, require_dist


def license_compatibility_filter(in_licenses):
    df = pd.read_csv(os.path.join('./app/knowledgebase/license_recommended.csv'))
    all_licenses = df['license'].tolist()

    compatible_both_list = df['license'].tolist()
    compatible_secondary_list = df['license'].tolist()
    compatible_combine_list = df['license'].tolist()
    df1 = pd.read_csv(os.path.join('./app/knowledgebase/compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    checked_list = []
    dual_no_checked_license = set()
    for licenseA in in_licenses:
        if len(licenseA) <=1:
            try:
                licenseA=licenseA[0]
            except:
                continue
            if licenseA in check_license_list:
                checked_list.append(licenseA)
                for licenseB in all_licenses:
                    compatibility_result = str(df1.loc[licenseA, licenseB])
                    if compatibility_result != '1,2':
                        if licenseB in compatible_both_list:
                            compatible_both_list.remove(licenseB)
                    if compatibility_result != '1' and compatibility_result != '1,2':
                        if licenseB in compatible_secondary_list:
                            compatible_secondary_list.remove(licenseB)
                    if compatibility_result != '2' and compatibility_result != '1,2':
                        if licenseB in compatible_combine_list:
                            compatible_combine_list.remove(licenseB)
        else:
            dual_checked = 0
            for licenseB in all_licenses:
                dual_licenses = licenseA
                is_remove = 1
                is_remove_both = 1
                is_remove_combine = 1
                is_remove_secondary = 1
                for sub_license in dual_licenses:
                    if sub_license in check_license_list:
                        compatibility_result = str(df1.loc[sub_license, licenseB])
                        dual_checked = 1
                        if compatibility_result != '0':
                            is_remove = 0
                        if compatibility_result == '1,2':
                            is_remove_both = 0
                        if compatibility_result == '1' or compatibility_result == '1,2':
                            is_remove_secondary = 0
                        if compatibility_result == '2' or compatibility_result == '1,2':
                            is_remove_combine = 0
                    else:
                        dual_no_checked_license.add(sub_license)
                if is_remove_both and licenseB in compatible_both_list and dual_checked == 1:
                    compatible_both_list.remove(licenseB)
                if is_remove_secondary and licenseB in compatible_secondary_list and dual_checked == 1:
                    compatible_secondary_list.remove(licenseB)
                if is_remove_combine and licenseB in compatible_combine_list and dual_checked == 1:
                    compatible_combine_list.remove(licenseB)
            if dual_checked == 1:
                checked_list.append(licenseA)
    #llist = list(set(sum(in_licenses,[])))
    compatible_licenses=list(set(compatible_both_list+compatible_secondary_list+compatible_combine_list))
    return compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list
    #return llist, checked_list, compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list,list(dual_no_checked_license)



def depend_detection(src_path,temp_path):
    output_depend_path = temp_path
    if os.path.exists(output_depend_path) == False:
        os.makedirs(output_depend_path)
    surport_lang = ["python","java","cpp","ruby","pom"]
    dependencies = []
    for lang in surport_lang: 
        # relative path need to be fixed
        proc = subprocess.Popen(
            ["java","-jar","./depends/depends.jar" ,"-d=" + output_depend_path , lang , src_path , lang + 'depend'])
        proc.communicate()
        proc.wait()
        project_name=src_path.split("/")[-1]
        if os.path.exists(output_depend_path + "/" + lang + "depend-file.json"):
            with open(output_depend_path + "/" + lang + "depend-file.json", 'r') as f:
                data = json.load(f)
                file_path_list = data['variables']
                dependencies_list = data['cells']
                for one_denpendence in dependencies_list:
                    src_index = one_denpendence['src']
                    dest_index = one_denpendence['dest']
                    src_file = file_path_list[src_index]
                    dest_file = file_path_list[dest_index] #src depends on dest
                    dependencies.append((os.path.abspath(src_file).replace(os.path.abspath(src_path),project_name) ,os.path.abspath(dest_file).replace(os.path.abspath(src_path),project_name)))
    return dependencies

def conflict_dection_compliance(res):
    root_license = res["LICENSE"][0]
    
    dep_incompatible = False
    df1 = pd.read_csv(os.path.join('./app/knowledgebase/compatibility_63.csv'), index_col=0)

    check_license_list = df1.index.tolist()
    confilct_copyleft_set = set()
    confilct_depend_dict = []
    if root_license not in check_license_list:
        return [f"The license ({root_license}) of this project is not within our knowledge scope. Please manually check for compliance."],[]

    for file in res:
        if file == "LICENSE": 
            continue
        for license in res[file]:
            if license in check_license_list:
                compatibility_result = compatibility_judge(license, root_license)
                if compatibility_result == '0':
                    if "dependency" in file:
                        dep_incompatible = True
                    confilct_copyleft_set.add(f"License {root_license} of the project and License {license} in {file} are not compatible.")
                    confilct_depend_dict.append({"src_file":"LICENSE","src_license":root_license,"dest_file":file,"dest_license":license})
    
    license_file={}
    for f in res:
        if f == "LICENSE" or "/" in f:  #skip dependencies
            for l in res[f]:
                license_file[l]=license_file.get(l,[])+[f]

    for lA in license_file:
        for lB in license_file:
            iscompatibility = 0
            ischeck = 0
            if lA in check_license_list and lB in check_license_list:
                ischeck = 1
                compatibility_result_ab = compatibility_judge(lA, lB)
                compatibility_result_ba = compatibility_judge(lB, lA)
                if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                    iscompatibility = 1
            if iscompatibility == 0 and ischeck == 1:
                fileAs=",".join(license_file[lA])
                fileBs=",".join(license_file[lB])
                if f"License {lA} in files({fileAs}) and License {lB} in files({fileBs}) are not compatible." not in confilct_copyleft_set and f"License {lB} in files({fileBs}) and License {lA} in files({fileAs}) are not compatible." not in confilct_copyleft_set:
                    confilct_copyleft_set.add(f"License {lA} in files({fileAs}) and License {lB} in files({fileBs}) are not compatible.")

    return list(confilct_copyleft_set),confilct_depend_dict,dep_incompatible

def conflict_dection(file_license_results,dependencies):
    df1 = pd.read_csv(os.path.join('./app/knowledgebase/compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    confilct_copyleft_set= set()
    confilct_depend_dict = []
    compatibility_result_ab = ''
    for dest_src in dependencies:
        src_file = dest_src[0]
        dest_file = dest_src[1]
        iscompatibility = 0
        ischeck = 0
        for licenseA in file_license_results.get(src_file,[]):
            for licenseB in file_license_results.get(dest_file,[]):
                if licenseA in check_license_list and licenseB in check_license_list:
                    ischeck = 1
                    compatibility_result_ab = compatibility_judge(licenseB,licenseA)
                if compatibility_result_ab != '0':
                    iscompatibility = 1
        if iscompatibility == 0 and ischeck == 1:
            confilct_depend_dict.append({"src_file":src_file,"src_license":licenseA,"dest_file":dest_file,"dest_license":licenseB})
    
    license_file={}
    for f in file_license_results:
        for l in file_license_results[f]:
            license_file[l]=license_file.get(l,[])+[f]

    for lA in license_file:
        for lB in license_file:
            iscompatibility = 0
            ischeck = 0
            if lA in check_license_list and lB in check_license_list:
                ischeck = 1
                compatibility_result_ab = compatibility_judge(lA, lB)
                compatibility_result_ba = compatibility_judge(lB, lA)
                if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                    iscompatibility = 1
            if iscompatibility == 0 and ischeck == 1:
                fileAs=",".join(license_file[lA])
                fileBs=",".join(license_file[lB])
                if f"License {lA} in files({fileAs}) and License {lB} in files({fileBs}) are not compatible." not in confilct_copyleft_set and f"License {lB} in files({fileBs}) and License {lA} in files({fileAs}) are not compatible." not in confilct_copyleft_set:
                    confilct_copyleft_set.add(f"License {lA} in files({fileAs}) and License {lB} in files({fileBs}) are not compatible.")
    print(confilct_copyleft_set)
    return list(confilct_copyleft_set),confilct_depend_dict

if __name__ == "__main__":
    licenses_in_files, dep_tree,require_dist=license_detection_files("/home/wwxu/RecLicense/backend/temp_files/2024-08-12 12:16:49.123700/test_project","/home/wwxu/RecLicense/backend/temp_files/2024-08-12 12:16:49.123700/test_project.json")
    # depends=depend_detection("/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie","/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie/temp.json")
    # print(res)
    # print(conflict_dection_compliance(res))
    
    #dependecy=depend_detection(unzip_path,unzip_path+"/temp.json")

    confilct_copyleft_list,confilct_depend_dict,dep_incompatible=conflict_dection_compliance(licenses_in_files)
    if dep_tree is not None and dep_incompatible:
        rem = get_remediation(mongo_uri = "mongodb://localhost:27017/",package='test_project',version="0.0.1",requires_dist=require_dist,dep_tree=dep_tree,license= licenses_in_files["LICENSE"][0])
        rem_lst = []
        for i in rem["changes"]:
            rem_lst.append(";".join(i))
    print(rem_lst)
    # license_compatibility_filter(res.values())
    #print(get_dependencies_licenses("/data/wwxu/PySC/backend/temp_files/2022-11-10 20:30:09.451573/hehao98_MigrationHelper"))
    pass