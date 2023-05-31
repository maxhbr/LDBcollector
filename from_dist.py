#!/usr/bin/env python3

# Regenerate the repository from the distributed shared.json file

import json
import re
import unicodedata

f = open("dist/shared.json", "r")
data = json.load(f)

licenses = {}
obligations = []
generics = []

for obj in data["objects"]:
    if obj["model"] == "cube.license":
        licenses[obj["fields"]["spdx_id"]] = obj["fields"]
        licenses[obj["fields"]["spdx_id"]]["obligations"] = []

    if obj["model"] == "cube.obligation":
        obligations.append(obj["fields"])

    if obj["model"] == "cube.generic":
        generics.append(obj["fields"])

print("licenses: ", len(licenses))
print("obligations: ", len(obligations))
print("generics: ", len(generics))

for obligation in obligations:
    spdx_id = obligation["license"][0]
    licenses[spdx_id]["obligations"].append(obligation)

for spdx_id, license_fields in licenses.items():
    file = open("./licenses/" + spdx_id + ".json", "w")
    json.dump(license_fields, file, indent=4)

for generic in generics:
    filename = unicodedata.normalize("NFKD", generic["name"])
    filename = re.sub(r"[^\w\s-]", "", filename).strip().lower()
    filename = re.sub(r"[-\s]+", "-", filename)
    file = open("./generics/" + filename + ".json", "w")
    json.dump(generic, file, indent=2)
