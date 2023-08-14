# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

SW_VERSION=0.1

PYTHON_DIR = os.path.dirname(os.path.realpath(__file__))
VAR_DIR = os.path.join(PYTHON_DIR, 'var')
LICENSE_DIR = os.path.join(VAR_DIR, 'licenses')

LICENSE_SCHEMA_FILE = os.path.join(VAR_DIR,'license_schema.json')
