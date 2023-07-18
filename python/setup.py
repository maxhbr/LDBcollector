from os import listdir
import os
from glob import glob
from json import load
from logging import debug
from config import LICENSE_DIR, VAR_DIR

from pathlib import Path

from jsonschema import validate

json_schema = None

def __validate_license_data(license_data):
    global json_schema
    if not json_schema:
        schema_file = os.path.join(VAR_DIR, "license_schema.json")
        debug(f'Reading JSON schema from {schema_file}')
        with open(schema_file) as f:
            json_schema = load(f)
    validate(instance=license_data, schema=json_schema)

def __read_license_file(license_file, check=False):
    with open(license_file) as f:
        data = load(f)
        if check:
            __validate_license_data(data)
            
        license_text_file = license_file.replace(".json", ".LICENSE")
        if not Path(license_text_file).is_file():
            raise FileNotFoundError(f'Could not find: {license_text_file}')
        with open(license_text_file) as lf:
            data['license_text'] = lf.read()
            
        return data

def license_info(license_name):
    license_file = os.path.join({LICENSE_DIR},".json")
    return __read_license_file(license_file)

def init_license_db(check=False):
    debug(f'reading from: {LICENSE_DIR}')
    for license_file in glob(f'{LICENSE_DIR}/*.json'):
        debug(f' * {license_file}')
        data = __read_license_file(license_file, check)
        debug(f' * {data}')
        
