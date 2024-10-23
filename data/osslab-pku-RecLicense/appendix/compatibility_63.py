from ensurepip import version
import pandas as pd



df = pd.read_csv('E:\\oss_license_selection_analyze\\src\\licenses_terms_63.csv',encoding='utf-8')
licenses = df['license'].tolist()
df1 = pd.DataFrame(columns=licenses)


for licenseA in licenses:
    linea = []

    licenseA_terms = df.loc[df['license']==licenseA].to_dict(orient='records')[0]
    restrictiveA = licenseA_terms['copyleft']
    versionA_str = licenseA_terms['compatible_version']
    secondaryA_str = licenseA_terms['secondary_license']  
    gpl_combineA_str = licenseA_terms['gpl_combine']
    if versionA_str != '0':
        versionA = versionA_str.split(',')
    else:
        versionA = None
    if secondaryA_str != '0':
        secondaryA = secondaryA_str.split(',')
    else:
        secondaryA = None   
    if gpl_combineA_str != '0':
        gpl_combineA = gpl_combineA_str.split(',')
    else:
        gpl_combineA = None 
    setA = set()
    if int(df.loc[df['license']==licenseA,'copyright']) == 0 or int(df.loc[df['license']==licenseA,'copyright']) == 1:
        setA.add('copyright')
    if int(df.loc[df['license']==licenseA,'retain_attr']) == 1:
        setA.add('retain_attr')
    if int(df.loc[df['license']==licenseA,'enhance_attr']) == 1:
        setA.add('enhance_attrA')
    if int(df.loc[df['license']==licenseA,'modification']) == 1:
        setA.add('modification')
    if int(df.loc[df['license']==licenseA,'interaction']) == 1:
        setA.add('interaction')
    if int(df.loc[df['license']==licenseA,'patent_term']) == 1:
        setA.add('patent_term')
    if int(df.loc[df['license']==licenseA,'acceptance']) == 1:
        setA.add('acception')
   
    for licenseB in licenses:
        restrictiveB = int(df.loc[df['license']==licenseB,'copyleft'])
        setB = set()
        if int(df.loc[df['license']==licenseB,'copyright']) == 0 or int(df.loc[df['license']==licenseB,'copyright']) == 1:
            setB.add('copyright')
        if int(df.loc[df['license']==licenseB,'retain_attr']) == 1:
            setB.add('retain_attr')
        if int(df.loc[df['license']==licenseB,'enhance_attr']) == 1:
            setB.add('enhance_attrB')
        if int(df.loc[df['license']==licenseB,'modification']) == 1:
            setB.add('modification')
        if int(df.loc[df['license']==licenseB,'interaction']) == 1:
            setB.add('interaction')
        if int(df.loc[df['license']==licenseB,'patent_term']) == 1:
            setB.add('patent_term')
        if int(df.loc[df['license']==licenseB,'acceptance']) == 1:
            setB.add('acceptance')

        

        # 从条款判断次级兼容和组合兼容
        if licenseA == licenseB:
            compatibility_AB = '1,2'
        else:
            if restrictiveA == 0:
                if restrictiveB == 0 or restrictiveB == 1:
                    if setA == setB:
                        compatibility_AB = '1,2'
                    elif setA.issubset(setB):
                        compatibility_AB = '1,2'
                    else:
                        if versionA != None and licenseB in versionA:
                            compatibility_AB = '1,2'
                        elif secondaryA != None and licenseB in secondaryA:
                            compatibility_AB = '1,2'
                        else:
                            compatibility_AB = '2'              
                elif restrictiveB == 2 or restrictiveB == 3:
                    if setA == setB:
                        compatibility_AB = '1'
                    elif setA.issubset(setB):
                        compatibility_AB = '1'
                    else:
                        if versionA != None and licenseB in versionA:
                            compatibility_AB = '1'
                        elif secondaryA != None and licenseB in secondaryA:
                            compatibility_AB = '1'                        
                        else:
                            compatibility_AB = '0'
            elif restrictiveA == 1 or restrictiveA == 2:
                if restrictiveB == 0:
                    compatibility_AB = '2'
                elif restrictiveB == 1:
                    if versionA != None and licenseB in versionA:
                        compatibility_AB = '1,2'
                    elif secondaryA != None and licenseB in secondaryA:
                        compatibility_AB = '1,2'
                    else:
                        compatibility_AB = '2'
                elif restrictiveB == 2 or restrictiveB == 3:
                    if versionA != None and licenseB in versionA:
                        if gpl_combineA != None and licenseB in gpl_combineA:
                            compatibility_AB = '1,2'
                        else:
                            compatibility_AB = '1'
                    elif secondaryA != None and licenseB in secondaryA:
                        if gpl_combineA != None and licenseB in gpl_combineA:
                            compatibility_AB = '1,2'
                        else:
                            compatibility_AB = '1'
                    else:
                        if gpl_combineA != None and licenseB in gpl_combineA:
                            compatibility_AB = '2'
                        else:
                            compatibility_AB = '0'                       
            elif restrictiveA == 3:  
                if versionA != None and licenseB in versionA:
                    if gpl_combineA != None and licenseB in gpl_combineA:
                        compatibility_AB = '1,2'
                    else:
                        compatibility_AB = '1'
                elif secondaryA != None and licenseB in secondaryA:  
                    if gpl_combineA != None and licenseB in gpl_combineA:
                        compatibility_AB = '1,2'
                    else:
                        compatibility_AB = '1'             
                else:
                    if gpl_combineA != None and licenseB in gpl_combineA:
                        compatibility_AB = '2'
                    else:
                        compatibility_AB = '0'
        linea.append(compatibility_AB)
        if licenseA == 'GPL-2.0+'and licenseB == 'GPL-3.0':
            print(compatibility_AB)

    df1.loc[len(df1)] = linea

df1.to_csv('E:\\oss_license_selection_analyze\\src\\compatibility_63.csv',encoding='utf-8')

