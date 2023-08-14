#!/usr/bin/env python3

import logging 

from license_db import LicenseDatabase

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
