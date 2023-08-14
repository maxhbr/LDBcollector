#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging 

from license_meta_db import LicenseDatabase

logging.basicConfig(level=logging.DEBUG)
ldb = LicenseDatabase(check=True)

l = ldb.licenses()
print(f'all  size: {len(l)}')

l = ldb.license("GPLv2+")
print(f'l: {l}')

l = ldb.license_scancode_key("GPLv2+")
print(f'l: {l}')

l = ldb.license_spdxid("GPLv2+")
print(f'l: {l}')
