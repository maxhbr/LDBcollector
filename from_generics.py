# SPDX-FileCopyrightText: 2024 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

# A temporary script to convert a `generics.json` file exported from the `/generics/`
# page in Hermine into individual generic files, inside a `tmp_generics` folder


import json
import os
import re
import unicodedata

from common import LICENSE_SHARED_FIELDS, GENERIC_SHARED_FIELDS

TMP_DIR_PATH = "./tmp_generics/"

if not os.path.exists(TMP_DIR_PATH):
    os.makedirs(TMP_DIR_PATH)

with open ("generics.json") as source_file:
    data = json.load(source_file)


generics = []

for obj in data:
    if obj["model"] == "cube.generic":
        generics.append(
            {
                key: value
                for key, value in obj["fields"].items()
                if key in GENERIC_SHARED_FIELDS
            }
        )

print("generics: ", len(generics))


for generic in generics:
    filename = unicodedata.normalize("NFKD", generic["name"])
    filename = re.sub(r"[^\w\s-]", "", filename).strip().lower()
    filename = re.sub(r"[-\s]+", "-", filename)
    file = open(TMP_DIR_PATH + filename + ".json", "w")
    json.dump(generic, file, indent=2)
