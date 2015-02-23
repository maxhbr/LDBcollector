import os

import requests

from oscad_data import load_data

texts_dir = os.path.join(os.path.dirname(__file__), 'data', 'texts')
baseurl = 'https://raw.githubusercontent.com/enyst/licenses-db/master/'

if __name__ == '__main__':
    details = load_data('license_details')

    for oscad_id, detail in details.items():
        licensedb_id = detail['licensedb_id']

        file = os.path.join(texts_dir, licensedb_id + '.txt')

        with open(file, 'w') as f:
            r = requests.get(baseurl + licensedb_id + '.txt', stream=True)
            for chunk in r.iter_content(4096):
                f.write(chunk)

        if oscad_id != licensedb_id:
            os.symlink(licensedb_id + '.txt',
                       os.path.join(texts_dir, oscad_id + '.txt'))
