import pandas as pd

# 2、许可证兼容性判断
def compatibility_judge(licenseA,licenseB):
    df = pd.read_csv('./app/konwledgebase/compatibility_63.csv', index_col=0)
    
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

def license_uncompatibility1_reason(licenseA,licenseB):
    reason = '不能次级兼容的原因是，'
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
        restrictiveA.add('Interaction')
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
        restrictiveB.add('Interaction')
    if licenseB_terms['patent_term'] == 1:
        restrictiveB.add('Patent termination')
    if licenseB_terms['acceptance'] == 1:
        restrictiveB.add('Acceptance')
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
def license_uncompatibility2_reason(licenseA,licenseB):
    reason = '不能组合兼容的原因是，'
    df = pd.read_csv("./app/konwledgebase/licenses_terms_63.csv")
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
        reason = reason + licenseB + '是' + licenseA + '次级兼容的后续版本。'
    if licenseB in secondaryA:
        reason = reason + licenseB + '在' + licenseA + '包含的次级许可证列表中，允许' + licenseA + '次级兼容' + licenseB + '。'
    if licenseB in combineA:
        reason = reason + licenseA + '与' + licenseB + '满足GPL系列许可证的组合兼容条件。'
    return reason

def license_compatibility_judge(licenseA,licenseB):
    compatibility_result = compatibility_judge(licenseA,licenseB)
    iscompatibility = ""
    how_to_use = ""
    why_or_why_not = ""
    compatibility_terms = []
    if licenseA == licenseB:
        iscompatibility = licenseA + "兼容" + licenseB + "。"
        why_or_why_not = "您选择了两个相同的许可证。"
    else:
        if compatibility_result == '0':
            iscompatibility = licenseA + "不兼容" + licenseB + "。"
            how_to_use = "您不能在" + licenseB + "授权的作品中使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品。"
            why_or_why_not,compatibility_terms = license_uncompatibility1_reason(licenseA, licenseB)
            why_or_why_not = "(1)" + why_or_why_not + "(2)" +license_uncompatibility2_reason(licenseA, licenseB)
        elif compatibility_result == '1':
            iscompatibility = licenseA + "次级兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您修改或使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" \
                         + "衍生作品的整体及其部分（包括原" + licenseA + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理。"
            why_or_why_not = license_uncompatibility2_reason(licenseA, licenseB)
        elif compatibility_result == '2':
            iscompatibility = licenseA + "组合兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您修改或使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品，所产生的衍生作品的整体可以采用" + licenseB + "授权，" \
                         + "但须确保该衍生作品中原" + licenseA + "授权的部分及其修改仍然受" + licenseA + "的约束，而" + licenseB + "约束除" + licenseA + "授权部分的其他部分。"
            why_or_why_not,compatibility_terms =  license_uncompatibility1_reason(licenseA, licenseB)
        elif compatibility_result == '1,2':
            iscompatibility = licenseA + "次级兼容且组合兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您可以任选一种兼容性场景进行许可证管理。（1）若您选择次级兼容，则" + "您修改或使用（包括但不限于链接、复制粘贴等方式）" \
                         + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" + "衍生作品的整体及其部分（包括原" + licenseA \
                         + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理；（2）若您选择组合兼容，则" + "您修改或使用（包括但不限于链接、复制粘贴等方式）" \
                         + licenseA + "授权的作品，所产生的衍生作品的整体可以采用" + licenseB + "授权，" + "但须确保该衍生作品中原" + licenseA \
                         + "授权的部分及其修改仍然受" + licenseA + "的约束，而" + licenseB + "约束除" + licenseA + "授权部分的其他部分。"
            why_or_why_not = ""
    return {"licenseA": licenseA,
                         "licenseB": licenseB,
                         "iscompatibility":iscompatibility,
                         "how_to_use":how_to_use,
                         "why_or_why_not":why_or_why_not,
                         "compatibility_terms":compatibility_terms,
                         }