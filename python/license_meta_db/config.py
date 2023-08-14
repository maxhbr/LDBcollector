# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

PYTHON_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
TOP_DIR = os.path.join(PYTHON_DIR, "..")
LICENSE_DIR = os.path.join(TOP_DIR, "licenses")
VAR_DIR = os.path.join(TOP_DIR, "var")

LICENSE_SCHEMA_FILE = "license_schema.json"
