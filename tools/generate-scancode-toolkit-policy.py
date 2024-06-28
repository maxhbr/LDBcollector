#!/usr/bin/python3

"""
Takes data from `fedora-license-data` JSON and prints licence policy file
for Scancode-toolkit:
https://scancode-toolkit.readthedocs.io/en/stable/plugins/licence_policy_plugin.html?highlight=policy#policy-file-specification
"""

import json
import sys
from licensedcode.cache import get_licenses_db

def extract_spdx_to_scancode_mapping():
    licenses_db = get_licenses_db()
    spdx_to_scancode = {}

    for key, license in licenses_db.items():
        spdx_id = license.spdx_license_key
        if spdx_id:
            spdx_to_scancode[spdx_id] = key

    return spdx_to_scancode


file_data = open(sys.argv[1], "r")
data = json.load(file_data)
scancode_data = extract_spdx_to_scancode_mapping()

licenses_list = []
print("license_policies:")
for license in data.values():
    license_item = license.get("license")
    if not license_item:
        continue
    if "allowed" in license_item["status"]:
        label = "Allowed License"
        color_code = "#BFED91"
        icon = "icon-ok-circle"
    elif "not-allowed" in license_item["status"]:
        label = "Not-allowed License"
        color_code = "#EDBF91"
        icon = "icon-warning-sign"
    else:
        label = "Allowed under conditions"
        color_code = "#EDED91"
        icon = "icon-question-sign"

    # if scancode does not now this expression then use the SPDX expression
    # FIXME this omits various expression with WITH, OR....
    license_key = scancode_data.get(license_item["expression"], license_item["expression"])
    if license_item:
        print(f"""-   license_key: {license_key}
    label: {label}
    color_code: {color_code}
    icon: {icon}""")
