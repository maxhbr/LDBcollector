#!/bin/env python3

# SPDX-FileCopyrightText: 2026 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# Validates license files against the JSON schema
#

import glob
import json
from jsonschema import validate

# read the JSON schema
with open('var/license_schema.json') as fp:
    json_schema = json.load(fp)

# validate a single file
def validate_license_file(filename):
    with open (filename) as fp:
        license_data = json.load(fp)
        validate(instance=license_data,
                 schema=json_schema)

# loop over all license files, and validate them
def test_license_files():
    for f in glob.glob('var/licenses/*.json'):
        validate_license_file(f)
