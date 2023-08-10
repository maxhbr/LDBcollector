#!/usr/bin/env python3

import logging 

from license_db import LicenseDatabase


logging.basicConfig(level=logging.DEBUG)
ldb = LicenseDatabase(check=True)

l = ldb.license_info_spdxid("GPL-2.0-or-later")
print(f'l: {l}')

l = ldb.licenses()
print(f'all  size: {len(l)}')

l = ldb.licenses(orgs=["Sandklef FOSS Labs AB"])
print(f'hesa size: {len(l)}')

l = ldb.licenses(orgs=["Sandklef GNU Labs"])
print(f'gnu size: {len(l)}')

l = ldb.licenses(orgs=["Sandklef GNU Labs", "Sandklef FOSS Labs AB"])
print(f'sandklef size: {len(l)}')

l = ldb.licenses(orgs=["Someone else"])
print(f'else size: {len(l)}')


