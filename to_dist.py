#!/usr/bin/env python3

# Generate the distributed shared.json file from the repository

import json
import os
from datetime import datetime
from common import LICENSE_SHARED_FIELDS, GENERIC_SHARED_FIELDS

objects = []
obligations = []


for filename in os.listdir("./generics"):
    if filename.endswith(".json"):
        file = open("./generics/" + filename, "r")
        generic_fields = json.load(file)
        objects.append(
            {
                "model": "cube.generic",
                "fields": {
                    key: value
                    for key, value in generic_fields.items()
                    if key in GENERIC_SHARED_FIELDS
                },
            }
        )


for filename in os.listdir("./licenses"):
    if filename.endswith(".json"):
        file = open("./licenses/" + filename, "r")
        license_fields = json.load(file)
        obligations.extend(license_fields["obligations"])
        del license_fields["obligations"]
        objects.append(
            {
                "model": "cube.license",
                "fields": {
                    key: value
                    for key, value in license_fields.items()
                    if key in LICENSE_SHARED_FIELDS
                },
            }
        )

for obligation in obligations:
    objects.append(
        {
            "model": "cube.obligation",
            "fields": obligation,
        }
    )


data = {
    "date": datetime.now().isoformat(),
    "version": "1.0",
    "objects": objects,
}

file = open("dist/shared.json", "w")
json.dump(data, file, indent=2)
