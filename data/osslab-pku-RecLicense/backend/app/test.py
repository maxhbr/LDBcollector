import subprocess
import json
import os
import pandas as pd 
import tqdm
def compatibility_judge(licenseA,licenseB):
    # relative path need to be fixed
    df = pd.read_csv('/data/wwxu/PySC/backend/app/knowledgebase/compatibility_63.csv', index_col=0)
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

def license_detection_files(file_path,output_path):
    results={}
    pipe = subprocess.Popen(
        ["scancode-toolkit/scancode","-l" ,"-n","10","--license-score","95","--json", output_path, file_path,"--license-text"],#relative path
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
                    licenses_spdx.append(license["spdx_license_key"])
                results[file["path"]]=list(set(licenses_spdx))

    return results

def license_compatibility_filter(in_licenses):
    df = pd.read_csv(os.path.join('/data/wwxu/PySC/backend/app/knowledgebase/license_recommended.csv'))
    all_licenses = df['license'].tolist()
    compatible_licenses = df['license'].tolist()
    compatible_both_list = df['license'].tolist()
    compatible_secondary_list = df['license'].tolist()
    compatible_combine_list = df['license'].tolist()
    df1 = pd.read_csv(os.path.join('/data/wwxu/PySC/backend/app/knowledgebase/compatibility_63.csv'), index_col=0)
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
                    if compatibility_result == '0':
                        if licenseB in compatible_licenses:
                            compatible_licenses.remove(licenseB)
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
                if is_remove and licenseB in compatible_licenses and dual_checked == 1:
                    compatible_licenses.remove(licenseB)
                if is_remove_both and licenseB in compatible_both_list and dual_checked == 1:
                    compatible_both_list.remove(licenseB)
                if is_remove_secondary and licenseB in compatible_secondary_list and dual_checked == 1:
                    compatible_secondary_list.remove(licenseB)
                if is_remove_combine and licenseB in compatible_combine_list and dual_checked == 1:
                    compatible_combine_list.remove(licenseB)
            if dual_checked == 1:
                checked_list.append(licenseA)
    llist = list(set(sum(in_licenses,[])))
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
            ["java","-jar","/data/wwxu/PySC/backend/depends/depends.jar" ,"-d=" + output_depend_path , lang , src_path , lang + 'depend'])
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
                    dependencies.append((src_file.replace(src_path,project_name) ,dest_file.replace(src_path,project_name)))
    return dependencies
#print(license_detection_files("/data/wwxu/PySC/test_scan","/data/wwxu/PySC/backend/temp_files/license.json"))
#print(depend_detection("/data/wwxu/PySC/ninka","/data/wwxu/PySC/backend/temp_files/ninka/"))
#print(depend_detection("/data/wwxu/PySC/backend/app","/data/wwxu/PySC/backend/temp_files/app/"))

def conflict_dection(file_license_results,dependencies):
    #relative path need to be fixed
    df1 = pd.read_csv(os.path.join('/data/wwxu/PySC/backend/app/knowledgebase/compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    confilct_copyleft_set= set()
    confilct_depend_dict = {}
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
            confilct_depend_dict[dest_file] = src_file+'的许可证'+licenseA+'不兼容'+dest_file+'的许可证'+licenseB

    
    for fileA in tqdm.tqdm(file_license_results):
        for fileB in file_license_results:
            iscompatibility = 0
            for lA in file_license_results[fileA]:
                for lB in file_license_results[fileB]:
                    if lA in check_license_list and lB in check_license_list:
                        ischeck = 1
                        compatibility_result_ab = compatibility_judge(lA, lB)
                        compatibility_result_ba = compatibility_judge(lB, lA)
                        if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                            iscompatibility = 1
            if iscompatibility == 0 and ischeck == 1:
                if fileA != fileB:
                    licenseA=" ".join(file_license_results[fileA])
                    licenseB=" ".join(file_license_results[fileB])
                    if f"{fileA}({licenseA}) and {fileB}({licenseB}) are not compatible." not in confilct_copyleft_set:
                        confilct_copyleft_set.add(f"{fileA}({licenseA}) and {fileB}({licenseB}) are not compatible.")
                else:
                    if f"Licenses in {fileA}({licenseA}) are not compatible." not in confilct_copyleft_set:
                        confilct_copyleft_set.add(f"Licenses in {fileA}({licenseA}) are not compatible.")

    return list(confilct_copyleft_set),confilct_depend_dict
#res=license_detection_files("/data/wwxu/PySC/backend/app","/data/wwxu/PySC/backend/temp_files/license.json")
# print(res)
#print(license_compatibility_filter(list(res.values())))
#dep=depend_detection("/data/wwxu/PySC/backend/app","/data/wwxu/PySC/backend/temp_files/backend/app/")
#print(dep)
# print(conflict_dection(res,dep,list(res.values())))

def license_incompatibility1_reason(licenseA,licenseB):
    reason = '不能次级兼容的原因是，'
    compatibility_terms = []
    df = pd.read_csv("/data/wwxu/PySC/backend/app/knowledgebase/licenses_terms_63.csv")
    licenseA_terms = df[df['license']==licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license']==licenseB].to_dict(orient='records')[0]
    restrictiveA = set()
    restrictiveB = set()
    if licenseA_terms['retain_attr'] == 1:
        restrictiveA.add('保留归属')
    if licenseA_terms['enhance_attr'] == 1:
        restrictiveA.add('增强归属')
    if licenseA_terms['modification'] == 1:
        restrictiveA.add('添加修改声明')
    if licenseA_terms['interaction'] == 1:
        restrictiveA.add('网络部署公开源码')
    if licenseA_terms['patent_term'] == 1:
        restrictiveA.add('专利诉讼终止')
    if licenseA_terms['acceptance'] == 1:
        restrictiveA.add('明确接受许可')
    if licenseB_terms['retain_attr'] == 1:
        restrictiveB.add('保留归属')
    if licenseB_terms['enhance_attr'] == 1:
        restrictiveB.add('增强归属')
    if licenseB_terms['modification'] == 1:
        restrictiveB.add('添加修改声明')
    if licenseB_terms['interaction'] == 1:
        restrictiveB.add('网络部署公开源码')
    if licenseB_terms['patent_term'] == 1:
        restrictiveB.add('专利诉讼终止')
    if licenseB_terms['acceptance'] == 1:
        restrictiveB.add('明确接受许可')
    if licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] != 0:
        reason = reason + licenseB + "是限制型开源许可证，如果使用（包括但不限于链接、复制粘贴等方式）了" + licenseA + "授权的作品，要求" + licenseA \
                 + "授权的作品将受" + licenseB + "的约束，而" + licenseA + "包含如下影响次级兼容的条款（" + licenseB + "中没有此等要求）" +"，使其不能在" + licenseB + "下再授权。"
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] == 0 :
        reason = reason + licenseA + "和" + licenseB + "都是宽松型开源许可证，但" + licenseA + "包含如下影响次级兼容的条款（" + licenseB + "中没有此等要求），使" + licenseA + "授权部分不能在" + licenseB + "下再授权。"
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] != 0:
        reason = reason + licenseA + "和" + licenseB + "都是限制型开源许可证，它们都包含copyleft的特性，且" + licenseB \
                 + "不是" + licenseA +"的兼容后续版本，也不是其兼容次级许可证，使" + licenseA + "授权部分不能在" +licenseB + \
                 "下再授权，进而无法满足" + licenseB + "的copyleft要求。"
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] == 0:
        reason = reason + licenseA + "是限制型开源许可证，而" + licenseB + "是宽松型开源许可证，修改或使用（包括但不限于链接、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，所产生的衍生作品须遵循" + licenseA + "的copyleft要求，使其不能在" + licenseB + "下再授权。"
    return reason,compatibility_terms

# 2、许可证兼容性判断工具页___许可证不组合兼容原因判断
def license_incompatibility2_reason(licenseA,licenseB):
    reason = '不能组合兼容的原因是，'
    df = pd.read_csv("/data/wwxu/PySC/backend/app/knowledgebase/licenses_terms_63.csv")
    licenseA_terms = df[df['license'] == licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license'] == licenseB].to_dict(orient='records')[0]
    if licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 2 :
        reason = reason + licenseB + "是库级弱限制型开源许可证，不限制通过接口调用该许可证授权作品的其他作品，但要求其约束部分（包括但不限于其包含的文件、其调用的组件等）都遵循其copyleft特性，若使用（包括但不限于调用、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，要求" + licenseA + "授权的部分须遵循" + licenseB + "的约束，因此无法满足组合兼容的场景。"
    elif licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 3 :
        reason = reason + licenseB + "是强限制型开源许可证，要求其授权作品的整体及其部分都遵循其copyleft特性，若使用（包括但不限于调用、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，要求" + licenseA + "授权的部分须遵循" + licenseB + "的约束，因此无法满足组合兼容的场景。"
    elif licenseA_terms['copyleft'] == 3:
        reason = reason + licenseA + "是强限制型开源许可证，要求其授权作品的整体及其部分都遵循其copyleft特性，因此无法满足组合兼容的场景。"
    return reason


# print(license_incompatibility1_reason("0BSD","MIT"))
