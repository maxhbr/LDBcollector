import pandas as pd

# 2、许可证兼容性判断
def compatibility_judge(licenseA,licenseB):
    df = pd.read_csv('./app/konwledgebase/compatibility_63.csv', index_col=0)
    
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

def license_uncompatibility1_reason(licenseA,licenseB):
    reason = 'The reason for why it is not secondarily compatible is that'
    compatibility_terms = []
    df = pd.read_csv("./app/konwledgebase/licenses_terms_63.csv")
    licenseA_terms = df[df['license']==licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license']==licenseB].to_dict(orient='records')[0]
    restrictiveA = set()
    restrictiveB = set()
    if licenseA_terms['copyright'] == 0 or licenseA_terms['copyright'] == 1:
        restrictiveA.add('Copyright')
    if licenseA_terms['retain_attr'] == 1:
        restrictiveA.add('Retain attribution')
    if licenseA_terms['enhance_attr'] == 1:
        restrictiveA.add('Enhance attribution')
    if licenseA_terms['modification'] == 1:
        restrictiveA.add('State changes')
    if licenseA_terms['interaction'] == 1:
        restrictiveA.add('Network deployments still need to open source the code')
    if licenseA_terms['patent_term'] == 1:
        restrictiveA.add('Patent termination')
    if licenseA_terms['acceptance'] == 1:
        restrictiveA.add('Acceptance')
    if licenseB_terms['copyright'] == 0 or licenseB_terms['copyright'] == 1:
        restrictiveB.add('Copyright')
    if licenseB_terms['retain_attr'] == 1:
        restrictiveB.add('Retain attribution')
    if licenseB_terms['enhance_attr'] == 1:
        restrictiveB.add('Enhance attribution')
    if licenseB_terms['modification'] == 1:
        restrictiveB.add('State changes')
    if licenseB_terms['interaction'] == 1:
        restrictiveB.add('Network deployments still need to open source the code')
    if licenseB_terms['patent_term'] == 1:
        restrictiveB.add('Patent termination')
    if licenseB_terms['acceptance'] == 1:
        restrictiveB.add('Acceptance')
    if licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] != 0:
        # reason = f"{reason} {licenseB} 是限制型开源许可证，如果使用（包括但不限于链接、复制粘贴等方式）了" + licenseA + "授权的作品，要求" + licenseA \
        #          + "授权的作品将受" + licenseB + "的约束，而" + licenseA + "包含如下影响次级兼容的条款（" + licenseB + "中没有此等要求）" +"，使其不能在" + licenseB + "下再授权。"
        reason = f"{reason} {licenseB} is a restricted license, and if a work licensed under {licenseB} uses (including but not limited to linking, copy-pasting and so on.) a work licensed under {licenseA}, the part originally licensed under {licenseA} is required to be be subject to {licenseB}. But {licenseA} contains provisions affecting secondary compatibility (which are not required under {licenseB}) that prevent it from being re-licensed under {licenseB}."
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] == 0 :
        reason = f"{reason} {licenseA} and {licenseB}  are both permissive open source licenses, but {licenseA} contains provisions affecting secondary compatibility (which are not required in MulanPSL-2.0) that make the part licensed under {licenseA} cannot be re-licensed under {licenseB}."
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] != 0:
        reason = f"{reason} {licenseA} and {licenseB} are restricted open source licenses, both of which contain copyleft features. {licenseB} \
                 is not a compatible successor to {licenseA}, nor is it a compatible sublicense, making the licensed portion of {licenseA} cannot be re-licensed under {licenseB}, and thus cannot meet the copyleft requirements of {licenseB}."
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] == 0:
        # reason = reason + licenseA + "是限制型开源许可证，而" + licenseB + "是宽松型开源许可证，修改或使用（包括但不限于链接、复制粘贴等方式）了" \
        #          + licenseA + "授权的作品，所产生的衍生作品须遵循" + licenseA + "的copyleft要求，使其不能在" + licenseB + "下再授权。"
        reason=f"{reason} {licenseA} is a restricted open source license, while {licenseB} is a permissive open source license. If modifying or using (including but not limited to linking, copy-pasting, etc.) a work licensed under {licenseA}, the derivative work is subject to the copyleft feature of {licenseA} so that it cannot be re-licensed under {licenseB}."
    return reason,compatibility_terms

# 2、许可证兼容性判断工具页___许可证不组合兼容原因判断
def license_uncompatibility2_reason(licenseA,licenseB):
    reason = 'The reason why it is not combinatively compatible is that'
    df = pd.read_csv("./app/konwledgebase/licenses_terms_63.csv")
    licenseA_terms = df[df['license'] == licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license'] == licenseB].to_dict(orient='records')[0]
    if licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 2 :
        # reason = reason + licenseB + "是库级弱限制型开源许可证，不限制通过接口调用该许可证授权作品的其他作品，但要求其约束部分（包括但不限于其包含的文件、其调用的组件等）都遵循其copyleft特性，若使用（包括但不限于调用、复制粘贴等方式）了" \
        #          + licenseA + "授权的作品，要求" + licenseA + "授权的部分须遵循" + licenseB + "的约束，因此无法满足组合兼容的场景。"
        reason=f"""{reason} {licenseB} is a library-level weakly restricted open source license, 
        which does not restrict other works from calling the work licensed under it through its interface,  
        but requires that the parts bound by it (including but not limited to the files the work contains, the components it calls, etc.) 
        all follow its copyleft feature. If a work licensed under {licenseA} is used (including but not limited to calling, copy-pasting, etc.), 
        the part originally licensed under {licenseA} is required to follow the constraints of {licenseB}, so it cannot meet the scenario of combinative compatibility."""
    elif licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 3 :
        reason = f"{reason} {licenseB} is a strong restrictive open source license, which requires the whole of its licensed work and its parts to follow its copyleft feature. If the work licensed by \
            {licenseA} is used (including but not limited to calling, copy-pasting, etc.), the part licensed by {licenseA} is required to follow the {licenseB} constraint, and therefore cannot meet the scenario of combinative compatibility."
    elif licenseA_terms['copyleft'] == 3:
        reason =f"{reason} {licenseA} is a strongly restrictive open source license that requires the whole of its licensed work and its parts to follow its copyleft feature, and therefore cannot meet the scenario of combinative compatibility."
    return reason


# 2、因版本兼容、次级许可证兼容、gpl组合兼容的原因
def license_compatibility3_reason(licenseA,licenseB):
    reason = ''
    versionA = []
    secondaryA = []
    combineA = []
    df = pd.read_csv("./app/konwledgebase/licenses_terms_63.csv")
    licenseA_terms = df[df['license'] == licenseA].to_dict(orient='records')[0]
    if licenseA_terms['compatible_version'] != '0':
        versionA = licenseA_terms['compatible_version'].split(',')
    if licenseA_terms['secondary_license'] != '0':
        secondaryA = licenseA_terms['secondary_license'].split(',')
    if licenseA_terms['gpl_combine'] != '0':
        combineA = licenseA_terms['gpl_combine'].split(',')
    if licenseB in versionA:
        reason = f"{reason} {licenseB} is a secondarily compatible successor to {licenseA}."
    if licenseB in secondaryA:
        reason = f"{reason} {licenseB} is in the list of secondary licenses of {licenseA}, so {licenseA} is secondarily compatible with {licenseB}."
    if licenseB in combineA:
        reason = f"{reason} {licenseA} and {licenseB} meet the combinative compatibility conditions of the GPL series licenses."
    return reason

def license_compatibility_judge(licenseA,licenseB):
    compatibility_result = compatibility_judge(licenseA,licenseB)
    iscompatibility = ""
    how_to_use = ""
    why_or_why_not = ""
    compatibility_terms = []
    if licenseA == licenseB:
        iscompatibility = licenseA + " is compatible with " + licenseB + "."
        why_or_why_not = "You choose two same licenses."
    else:
        if compatibility_result == '0':
            iscompatibility = licenseA + " is uncompatible with " + licenseB + "."
            #how_to_use = "You can not" + licenseB + "授权的作品中使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品。"
            how_to_use = f"You may not use (including but not limited to linking, copy-pasting and so on) the work licensed under {licenseA} in the work licensed under {licenseB} ."
            why_or_why_not,compatibility_terms = license_uncompatibility1_reason(licenseA, licenseB)
            why_or_why_not = "(1)" + why_or_why_not + "(2)" +license_uncompatibility2_reason(licenseA, licenseB)
        elif compatibility_result == '1':
            iscompatibility = licenseA + " is secondarily compatible with " + licenseB + "."
            # how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您修改或使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" \
            #              + "衍生作品的整体及其部分（包括原" + licenseA + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理。"
            how_to_use=license_compatibility3_reason(licenseA,licenseB)+ f"The derivative work resulting from your modification or use (including but not limited to linking, copy-pasting and so on) of works licensed under {licenseA} can be licensed under {licenseB}, and the derivative work as a whole and its parts (including the part originally licensed under {licenseA}) will be subject to {licenseB}. Please pay attention to the management of license information."
            why_or_why_not = license_uncompatibility2_reason(licenseA, licenseB)
            
        elif compatibility_result == '2':
            iscompatibility = licenseA + " is combinatively compatible with " + licenseB + "."
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + f"You can modify or use (including but not limited to linking, copy-pasting and so on) a work licensed under {licenseA}, and the resulting derivative work can be licensed under {licenseB} as a whole, provided that you ensure that the part of the derivative work originally licensed under {licenseA} and its modifications remain subject to {licenseA}, and that all parts other than that licensed under {licenseA} are subject to {licenseB}."
            why_or_why_not,compatibility_terms =  license_uncompatibility1_reason(licenseA, licenseB)
        elif compatibility_result == '1,2':
            iscompatibility = licenseA + " is both secondarily compatible and combinatively compatible with " + licenseB + "."
            how_to_use = f"{license_compatibility3_reason(licenseA,licenseB)} You can choose any of the compatibility scenarios for license management. (1) If you choose secondary compatibility, you modify or use (including but not limited to linking, copy-pasting, etc.) the work licensed by {licenseA}, the resulting derivative work can be licensed under {licenseB}, and the whole of derivative work and its parts (including the part originally licensed under {licenseA}) will be subject to {licenseB}. Please pay attention to the management of license information; (2) If you choose combinative compatibility, you modify or use (including but not limited to linking, copy-pasting, etc.) the work licensed under {licenseA}, the whole of the resulting derivative work can be licensed under {licenseB}, provided that you ensure that the part of the derivative work originally licensed under {licenseA} and its modifications remain subject to the {licenseA}, and {licenseB} binds all parts of the derivative work other than those licensed under {licenseA}."
            #  + "您可以任选一种兼容性场景进行许可证管理。（1）若您选择次级兼容，则" + "您修改或使用（包括但不限于链接、复制粘贴等方式）" \
            #              + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" + "衍生作品的整体及其部分（包括原" + licenseA \
            #              + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理；（2）若您选择组合兼容，则" + "您修改或使用（包括但不限于链接、复制粘贴等方式）" \
            #              + licenseA + "授权的作品，所产生的衍生作品的整体可以采用" + licenseB + "授权，" + "但须确保该衍生作品中原" + licenseA \
            #              + "授权的部分及其修改仍然受" + licenseA + "的约束，而" + licenseB + "约束除" + licenseA + "授权部分的其他部分。"
            why_or_why_not = ""
    return {"licenseA": licenseA,
                         "licenseB": licenseB,
                         "iscompatibility":iscompatibility,
                         "how_to_use":how_to_use,
                         "why_or_why_not":why_or_why_not,
                         "compatibility_terms":compatibility_terms,
                         }