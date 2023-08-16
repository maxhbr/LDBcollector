# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simple class
"""
import glob
import json
import logging
import os
from pathlib import Path

from flimea.config import LICENSE_DIR, LICENSE_SCHEMA_FILE, VAR_DIR
from flimea.exception import LicenseDatabaseError
from jsonschema import validate

json_schema = None

COMPATIBILITY_AS_TAG = 'compatibility_as'
IDENTIFIED_LICENSE_TAG = 'identified_license'
SCANCODE_KEY_TAG = 'scancode_key'
SCANCODE_KEYS_TAG = 'scancode_keys'
LICENSES_TAG = 'licenses'
ALIASES_TAG = 'aliases'
NAME_TAG = 'name'

class LicenseDatabase:

    def __init__(self, check=False, license_dir=LICENSE_DIR, logging_level=logging.INFO):
        logging.basicConfig(level=logging_level)
        self.license_dir = license_dir
        self.__init_license_db(check)

    def __validate_license_data(self, license_data):
        global json_schema
        if not json_schema:
            schema_file = LICENSE_SCHEMA_FILE
            logging.debug(f'Reading JSON schema from {schema_file}')
            with open(schema_file) as f:
                json_schema = json.load(f)
        validate(instance=license_data, schema=json_schema)

    def __read_license_file(self, license_file, check=False):
        with open(license_file) as f:
            data = json.load(f)
            if check:
                self.__validate_license_data(data)

            license_text_file = license_file.replace('.json', '.LICENSE')
            if not Path(license_text_file).is_file():
                raise FileNotFoundError(f'Could not find "{license_text_file}" matching "{license_file}"')
            with open(license_text_file) as lf:
                data['license_text'] = lf.read()

            return data

    def __init_license_db(self, check=False):
        self.license_db = {}
        licenses = {}
        aliases = {}
        scancode_keys = {}
        logging.debug(f'reading from: {self.license_dir}')
        for license_file in glob.glob(f'{self.license_dir}/*.json'):
            logging.debug(f' * {license_file}')
            data = self.__read_license_file(license_file, check)
            licenses[data['spdxid']] = data
            for alias in data[ALIASES_TAG]:
                aliases[alias] = data['spdxid']
            if SCANCODE_KEY_TAG in data:
                scancode_keys[data[SCANCODE_KEY_TAG]] = data['spdxid']

        self.license_db[LICENSES_TAG] = licenses
        self.license_db[ALIASES_TAG] = aliases
        self.license_db[SCANCODE_KEYS_TAG] = scancode_keys

    def __identify_license(self, name):
        if name in self.license_db[LICENSES_TAG]:
            ret_name = name
            ret_id = 'direct'
        elif name in self.license_db[ALIASES_TAG]:
            ret_name = self.license_db[ALIASES_TAG][name]
            ret_id = 'alias'
        elif name in self.license_db[SCANCODE_KEYS_TAG]:
            ret_name = self.license_db[SCANCODE_KEYS_TAG][name]
            ret_id = 'scancode_key'
        else:
            raise LicenseDatabaseError(f'Could not identify license from "{name}"')

        return {
            'queried_name': name,
            'name': ret_name,
            'identified_via': ret_id,
        }

    def licenses(self):
        return self.license_db[LICENSES_TAG].keys()

    def license(self, name):
        """
        name: spdx identifier, alias or scancode key

        returns the corresponding license object
        """
        identified_license = self.__identify_license(name)
        identified_name = identified_license[NAME_TAG]
        return {
            IDENTIFIED_LICENSE_TAG: identified_license,
            'license': self.license_db[LICENSES_TAG][identified_name],
        }

    def license_spdxid(self, name):
        """
        name: spdx identifier, alias or scancode key

        returns the corresponding spdxid
        """
        return self.license(name)['license']['spdxid']

    def license_scancode_key(self, name):
        """
        name: spdx identifier, alias or scancode key

        returns the corresponding scancode_key
        """
        return self.license(name)['license']['scancode_key']

    def compatibility_as_list(self):
        # List all compatibility_as that exist
        licenses = self.license_db[LICENSES_TAG]
        return [{COMPATIBILITY_AS_TAG: licenses[x][COMPATIBILITY_AS_TAG], 'spdxid': licenses[x]["spdxid"] }  for x in licenses if COMPATIBILITY_AS_TAG in licenses[x]]

    def aliases_list(self):
        # List all aliases that exist
        return self.license_db[ALIASES_TAG]

    def aliases(self, license_name):
        # List aliases for license identified by license_name
        identified_name = self.__identify_license(license_name)[NAME_TAG]
        return self.license_db[LICENSES_TAG][identified_name][ALIASES_TAG]

    def compatibility_as(self, license_name):
        # List compatibility_as for license
        identified = self.__identify_license(license_name)
        identified_name = identified[NAME_TAG]

        if COMPATIBILITY_AS_TAG in self.license_db[LICENSES_TAG][identified_name]:
            compat_as = self.license_db[LICENSES_TAG][identified_name][COMPATIBILITY_AS_TAG]
        else:
            compat_as = identified_name

        return {
            IDENTIFIED_LICENSE_TAG: identified,
            COMPATIBILITY_AS_TAG: compat_as,
        }
