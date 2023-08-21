#!/usr/bin/python3

"""
Takes data from `fedora-license-data` and prints the list of SPDX abbrevs of
ALL licenses. Including not allowed.
"""

import json
import sys

file_data = open(sys.argv[1], "r")
data = json.load(file_data)

licenses_list = []
for license in data.values():
    license_item = license.get("license")
    if license_item:
        licenses_list.append(license_item["expression"])

print('\n'.join(set(licenses_list)))

