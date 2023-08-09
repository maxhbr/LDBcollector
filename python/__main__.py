#!/usr/bin/env python3

import logging 

from license_db import LicenseDatabase


logging.basicConfig(level=logging.DEBUG)
ldb = LicenseDatabase(check=True)

l = ldb.license_info_spdxid("GPL-2.0-or-later")
print(f'l: {l}')

l = ldb.licenses()
print(f'all  size: {len(l)}')

l = ldb.licenses(["Henrik Sandklef <hesa@sandklef.com>"])
print(f'hesa size: {len(l)}')

l = ldb.licenses(["Someone else"])
print(f'else size: {len(l)}')


