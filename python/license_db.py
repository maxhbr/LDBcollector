from os import listdir
import os
from glob import glob
from json import load
from logging import debug
from config import LICENSE_DIR, VAR_DIR

from pathlib import Path

from jsonschema import validate

from exception import LicenseDBException

json_schema = None

class LicenseDatabase:

    def __init__(self, check=False):
        self.__init_license_db(check)

    
    def __validate_license_data(self, license_data):
        global json_schema
        if not json_schema:
            schema_file = os.path.join(VAR_DIR, "license_schema.json")
            debug(f'Reading JSON schema from {schema_file}')
            with open(schema_file) as f:
                json_schema = load(f)
        validate(instance=license_data, schema=json_schema)

    def __read_license_file(self, license_file, check=False):
        with open(license_file) as f:
            data = load(f)
            if check:
                self.__validate_license_data(data)

            license_text_file = license_file.replace(".json", ".LICENSE")
            if not Path(license_text_file).is_file():
                raise FileNotFoundError(f'Could not find: {license_text_file}')
            with open(license_text_file) as lf:
                data['license_text'] = lf.read()

            return data

    def __init_license_db(self, check=False):
        self.license_db = {}
        debug(f'reading from: {LICENSE_DIR}')
        for license_file in glob(f'{LICENSE_DIR}/*.json'):
            debug(f' * {license_file}')
            data = self.__read_license_file(license_file, check)
            #debug(f' * {data}')
            self.license_db[data['spdxid']] = data                

    def licenses(self, orgs=None):
        if not orgs:
            return self.license_db
        ret_list = []
        for org in orgs:
            ret_list += [l for l in self.license_db.values() if org in l["meta"]["organization"] ]

        return ret_list
            
    def license_info_spdxid(self, spdxid=None):
        if spdxid not in self.license_db:
            raise LicenseDBException(f'"{spdxid}" not present in license database.')
            
        return self.license_db[spdxid]
        
