# SPDX-FileCopyrightText: 2025 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: Unlicense
# A script to ensure consistency of the json files.

import json
import os


def lint_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    with open(file_path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


for dirpath, dirnames, filenames in os.walk("licenses"):
    for filename in filenames:
        lint_file(os.path.join(dirpath, filename))
for dirpath, dirnames, filenames in os.walk("generics"):
    for filename in filenames:
        lint_file(os.path.join(dirpath, filename))
