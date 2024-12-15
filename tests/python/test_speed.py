#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Before rewrite
# -------------------
# real    0m47,035s
# user    0m47,018s
# sys     0m0,013s

# After rewrite
# -------------------
# real    0m0,465s
# user    0m0,452s
# sys     0m0,013s

# so for consecutive calls, a call now takes 1% of what it took before


from flame.license_db import FossLicenses
fl = FossLicenses()



for lic in [ "MIT", "BSD-3-Clause", "GPL-2.0-or-later" , "GPL-2.0-only" ]:
    lic_obj = fl.license_complete(lic)
    print(f'{lic}: ', end='')
    for alias in lic_obj['aliases']:
        expression = fl.expression_license(alias, update_dual=False)
        assert lic == expression['identified_license']
        print('.', end='')
    print()
        

