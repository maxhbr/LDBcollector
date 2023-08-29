# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simple class
"""
import glob
import json
import logging
import re
from pathlib import Path

from flame.config import LICENSE_DIR, LICENSE_OPERATORS_FILE, LICENSE_SCHEMA_FILE
from flame.exception import LicenseDatabaseError
from jsonschema import validate

json_schema = None

COMPATIBILITY_AS_TAG = 'compatibility_as'
COMPATIBILITY_TAG = 'compatibility'
IDENTIFIED_ELEMENT_TAG = 'identified_element'
SCANCODE_KEY_TAG = 'scancode_key'
SCANCODE_KEYS_TAG = 'scancode_keys'
LICENSES_TAG = 'licenses'
ALIASES_TAG = 'aliases'
NAME_TAG = 'name'

LICENSE_OPERATORS_TAG = 'license_operators'

class LicenseDatabase:

    def __init__(self, check=False, license_dir=LICENSE_DIR, logging_level=logging.INFO):
        logging.basicConfig(level=logging_level)
        self.license_dir = license_dir
        self.__init_license_db(check)

    def __read_json(self, file_name):
        with open(file_name) as f:
            return json.load(f)

    def __validate_license_data(self, license_data):
        global json_schema
        if not json_schema:
            schema_file = LICENSE_SCHEMA_FILE
            logging.debug(f'Reading JSON schema from {schema_file}')
            json_schema = self.__read_json(schema_file)
        validate(instance=license_data, schema=json_schema)

    def __read_license_file(self, license_file, check=False):
        data = self.__read_json(license_file)
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
                if alias in aliases:
                    raise LicenseDatabaseError(f'Alias "{alias}" -> {data["spdxid"]} already defined as "{aliases[alias]}".')

                aliases[alias] = data['spdxid']
            if SCANCODE_KEY_TAG in data:
                scancode_keys[data[SCANCODE_KEY_TAG]] = data['spdxid']

        self.license_db[LICENSES_TAG] = licenses
        self.license_db[ALIASES_TAG] = aliases
        self.license_db[SCANCODE_KEYS_TAG] = scancode_keys
        self.license_db[SCANCODE_KEYS_TAG] = scancode_keys
        self.license_db[LICENSE_OPERATORS_TAG] = self.__read_json(LICENSE_OPERATORS_FILE)['operators']
        # regular expression for splitting expression in to parts
        re_list = [re.escape(op) for op in self.license_db[LICENSE_OPERATORS_TAG]]
        # make sure to && and || before & and | by sorting reverse
        re_list.sort(reverse=True)
        self.license_operators_re = '(' + '|'.join(re_list) + ')'

    def __identify_license(self, name):
        if name in self.license_db[LICENSES_TAG]:
            ret_name = name
            ret_id = 'direct'
        elif name in self.license_db[LICENSE_OPERATORS_TAG]:
            ret_name = self.license_db[LICENSE_OPERATORS_TAG][name]
            ret_id = 'operator'
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

    def expression_license(self, license_expression):
        new_expression = license_expression
        license_parts = []
        license_list = []
        for le in re.split(r'%s' % self.license_operators_re, new_expression):
            le = le.strip()
            if len(le) == 0:
                continue
            license_parts.append(self.license(le.strip()))
            license_list.append(self.license(le.strip())[IDENTIFIED_ELEMENT_TAG]['name'])
        new_expression = ' '.join(license_list).strip()
        return {
            'queried_license': license_expression,
            'identified_license': new_expression,
            'identifications': license_parts
        }

    def licenses(self):
        return list(self.license_db[LICENSES_TAG].keys())

    def license(self, name):
        """
        name: spdx identifier, alias or scancode key

        returns the corresponding license object
        """
        identified_license = self.__identify_license(name)
        identified_name = identified_license[NAME_TAG]
        if identified_license['identified_via'] == 'operator':
            return {
                IDENTIFIED_ELEMENT_TAG: identified_license,
                'operator': True
            }
        else:
            return {
                IDENTIFIED_ELEMENT_TAG: identified_license,
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
        return [{COMPATIBILITY_AS_TAG: licenses[x][COMPATIBILITY_AS_TAG], 'spdxid': licenses[x]['spdxid']} for x in licenses if COMPATIBILITY_AS_TAG in licenses[x]]

    def aliases_list(self, alias_license=None):
        if alias_license:
            return {k: v for k, v in self.license_db[ALIASES_TAG].items() if alias_license in v}
        # List all aliases that exist
        return self.license_db[ALIASES_TAG]

    def aliases(self, license_name):
        # List aliases for license identified by license_name
        identified_name = self.__identify_license(license_name)[NAME_TAG]
        return self.license_db[LICENSES_TAG][identified_name][ALIASES_TAG]

    def operators(self):
        return self.license_db[LICENSE_OPERATORS_TAG]

    def compatibility_as(self, license_name):
        # List compatibility_as for license
        identified = self.__identify_license(license_name)
        identified_name = identified[NAME_TAG]

        if COMPATIBILITY_AS_TAG in self.license_db[LICENSES_TAG][identified_name]:
            compat = self.license_db[LICENSES_TAG][identified_name][COMPATIBILITY_AS_TAG]
            method = COMPATIBILITY_AS_TAG
        else:
            compat = identified_name
            method = 'direct'

        return {
            IDENTIFIED_ELEMENT_TAG: identified,
            COMPATIBILITY_TAG: {
                'compat_as': compat,
                'queried_name': license_name,
                'identified_via': method
            }
        }

    def expression_compatibility_as(self, license_expression):
        expression_full = self.expression_license(license_expression)
        compats = []
        for identification in expression_full['identifications']:
            lic_elem = identification['identified_element']['name']
            if 'operator' in identification:
                compats.append({
                    'license_identification': identification,
                    'compat_identification': 'operator',
                    'compat_element': lic_elem,
                    'name': lic_elem
                })
            else:
                compat = self.compatibility_as(lic_elem)
                compats.append({
                    'license_identification': identification,
                    'compat_identification': compat,
                    'compat_element': compat,
                    'name': compat['compatibility']['compat_as']
                })

        compat_string = ' '.join([elem['name'] for elem in compats])

        return {
            'compatibilities': compats,
            'queried_license': license_expression,
            'identified_license': expression_full['identified_license'],
            'compat_license': compat_string
        }
