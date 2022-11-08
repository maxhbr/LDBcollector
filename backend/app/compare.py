import pandas as pd

def license_compare(compare_licenselist):
    df = pd.read_csv('/data/wwxu/PySC/backend/app/konwledgebase/licenses_terms_63.csv')
    df = df.query('license in '+str(compare_licenselist))
    result_list = df.to_dict(orient='records')

    return result_list

#print(license_compare(["MIT","MulanPSL-2.0","GPL-2.0-only"]))