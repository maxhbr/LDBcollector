#!/usr/bin/env python3

# Generate the distributed shared.json file from the repository

import json
import os
from datetime import datetime

objects = []
obligations = []

for filename in os.listdir("./generics"):
    if filename.endswith(".json"):
        file = open("./generics/" + filename, "r")
        generic_fields = json.load(file)
        objects.append(
            {
                "model": "cube.generic",
                "fields": generic_fields,
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
                "fields": license_fields,
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
