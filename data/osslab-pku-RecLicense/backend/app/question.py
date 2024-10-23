import pandas as pd
def license_terms_choice(answer):
    df = pd.read_csv("./app/knowledgebase/licenses_terms_63.csv")
    licenses_spdx = df['license'].tolist()
    licenses_copyleft = df['copyleft'].tolist()
    licenses_copyright = df['copyright'].tolist()
    licenses_patent = df['patent'].tolist()
    licenses_patent_term = df['patent_term'].tolist()
    licenses_trademark = df['trademark'].tolist()
    licenses_interaction = df['interaction'].tolist()
    licenses_modification = df['modification'].tolist()
    df2 = pd.read_csv("./app/knowledgebase/license_recommended.csv")
    init_licenselist=df2['license'].tolist()
    # 初始化推荐列表
    licenselist_recommended = init_licenselist[:]
    # 满足各个条款的列表的列表
    rr_license = []
    # 是否显示问题2
    q2_show = 1
    if answer[0] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[0] == "1":#'宽松型开源许可证'
            q2_show = 0
            for i, x in enumerate(licenses_copyleft):
                if x == 0 and licenses_copyright[i] != -1:
                    license_ok.append(licenses_spdx[i])
        elif answer[0] == "2":#'限制型开源许可证'
            for i, x in enumerate(licenses_copyleft):
                if x > 0:
                    license_ok.append(licenses_spdx[i])
        elif answer[0] == "3":#'公共领域许可证'
            q2_show = 0
            for i, x in enumerate(licenses_copyright):
                if x == -1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
    else:
        rr_license.append(init_licenselist[:])
    if q2_show == 1 and answer[1] != "" :
        # 满足该条款的许可证列表
        license_ok = []
        if answer[1] == "1": #'文件级__弱限制型开源许可证'
            for i, x in enumerate(licenses_copyleft):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        elif answer[1] == "2":#'库级__弱限制型开源许可证'
            for i, x in enumerate(licenses_copyleft):
                if x == 2:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_copyleft):
                if x == 3:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
    else:
        rr_license.append(init_licenselist[:])
    if answer[2] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[2] == "1": #'不提及专利权'
            for i, x in enumerate(licenses_patent):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        elif answer[2] == "2": #'明确授予专利权':
            for i, x in enumerate(licenses_patent):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent):
                if x == -1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        
    else:
        rr_license.append(init_licenselist[:])
        
    if answer[3] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[3] =="1":  #'包含反专利诉讼条款'
            for i, x in enumerate(licenses_patent_term):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent_term):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
    else:
        rr_license.append(init_licenselist[:])

    if answer[4] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[4] == "1": #'不提及商标权'
            for i, x in enumerate(licenses_trademark):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_trademark):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
    else:
        rr_license.append(init_licenselist[:])
    if answer[5] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[5] == "1": #'网络部署公开源码'
            for i, x in enumerate(licenses_interaction):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_interaction):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
    else:
        rr_license.append(init_licenselist[:])
    if answer[6] != "":
        # 满足该条款的许可证列表
        license_ok = []
        if answer[6] == "1":#'包含修改说明条款'
            for i, x in enumerate(licenses_modification):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_modification):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)

    else:
        rr_license.append(init_licenselist[:])


    for i in range(7):
        licenselist_recommended = sorted(list(set(licenselist_recommended) & set(rr_license[i])))

    return licenselist_recommended

