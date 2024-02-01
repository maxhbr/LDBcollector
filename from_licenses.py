# SPDX-FileCopyrightText: 2024 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

# A temporary script to convert a `licenses.json` file exported from the `/licenses/`
# page in Hermine into individual license files, inside a `tmp_licenses` folder


import json
import os

from common import LICENSE_SHARED_FIELDS

TMP_DIR_PATH = "./tmp_licenses/"

if not os.path.exists(TMP_DIR_PATH):
    os.makedirs(TMP_DIR_PATH)

with open("licenses.json") as source_file:
    data = json.load(source_file)


licenses = {}
obligations = []

for obj in data:
    if obj["model"] == "cube.license":
        licenses[obj["fields"]["spdx_id"]] = {
            key: value
            for key, value in obj["fields"].items()
            if key in LICENSE_SHARED_FIELDS
        }
        licenses[obj["fields"]["spdx_id"]]["obligations"] = []

    if obj["model"] == "cube.obligation":
        obligations.append(obj["fields"])

print("licenses: ", len(licenses))
print("obligations: ", len(obligations))

for obligation in obligations:
    spdx_id = obligation["license"][0]
    licenses[spdx_id]["obligations"].append(obligation)

for spdx_id, license_fields in licenses.items():
    file = open(TMP_DIR_PATH + spdx_id + ".json", "w")
    json.dump(license_fields, file, indent=4)
