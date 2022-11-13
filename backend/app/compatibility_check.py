import subprocess
import json
import os
import pandas as pd 
import tqdm
from .parse_dependency import *
import pymongo
mongo_client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
mongo_db = mongo_client['libraries']
mongo_collection = mongo_db['projects']

def compatibility_judge(licenseA,licenseB):
    df = pd.read_csv('./app/konwledgebase/compatibility_63.csv', index_col=0)
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

def license_detection_files(file_path,output_path):
    results={}
    pipe = subprocess.Popen(
        ["../scancode-toolkit/scancode","-l" ,"-n","10","--license-score","95","--json", output_path, file_path,"--license-text"],#relative path
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
                results[file["path"]]=list(set(licenses_spdx))
    dep_license=get_dependencies_licenses(file_path)
    results.update(dep_license)
    return results

def get_dependencies_licenses(file_path):
    dep_license={}
    dep=traverse(os.path.abspath(file_path))
    for lang in dep:
        for p in dep[lang]:
            if lang !="JavaScript":
                res=mongo_collection.find_one({"Name":p,"Language":lang})
            else:
                res=mongo_collection.find_one({ "$or" : [{"Name":p,"Language":"JavaScript"},{"Name":p,"Language":"TypeScript"} ]})
            if res:
                if "," in res['Licenses']:
                    dep_license[f"dependency({p})"]=res['Licenses'].split(",")
                else:
                    dep_license[f"dependency({p})"]=[res['Licenses']]
    return dep_license


def license_compatibility_filter(in_licenses):
    df = pd.read_csv(os.path.join('./app/konwledgebase/license_recommended.csv'))
    all_licenses = df['license'].tolist()

    compatible_both_list = df['license'].tolist()
    compatible_secondary_list = df['license'].tolist()
    compatible_combine_list = df['license'].tolist()
    df1 = pd.read_csv(os.path.join('./app/konwledgebase/compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    checked_list = []
    dual_no_checked_license = set()
    for licenseA in in_licenses:
        if len(licenseA) <=1:
            licenseA=licenseA[0]
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



def conflict_dection(file_license_results,dependencies):
    df1 = pd.read_csv(os.path.join('./app/konwledgebase/compatibility_63.csv'), index_col=0)
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
    # res=license_detection_files("/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie","/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie.json")
    # depends=depend_detection("/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie","/data/wwxu/PySC/backend/temp_files/2022-11-11 02:25:40.773691/Easesgr_reggie/temp.json")
    # print(conflict_dection(res,depends))
    # license_compatibility_filter(res.values())
    #print(get_dependencies_licenses("/data/wwxu/PySC/backend/temp_files/2022-11-10 20:30:09.451573/hehao98_MigrationHelper"))
    pass