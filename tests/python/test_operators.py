# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.license_db import FossLicenses
from flame.exception import FlameException
import logging
import sys

fl = FossLicenses(config={
    'level': 'logging.INFO'})

logger = logging.getLogger("test_values")
logging.basicConfig(encoding='utf-8', level=logging.INFO)

def __test_impl_sub(lic_expr, expected_lic):
    lic = fl.expression_license(lic_expr, update_dual=False)
    #print(f'lic: {lic}', file=sys.stderr)
    logging.debug(f'assert {lic["identified_license"]} == {expected_lic}')
    assert lic['identified_license'] == expected_lic
    print(f'OK: {lic}', file=sys.stderr)
    
def __test_impl(lic_expr1, lic_op, lic_expr2, expected_lic, addons):
    for pre in addons:
        for post in addons:
            print(f'TEST: {lic_expr1}{pre}{lic_op}{post}{lic_expr2}', file=sys.stderr)
            __test_impl_sub(f'{lic_expr1}{pre}{lic_op}{post}{lic_expr2}', expected_lic)


def test_and_mit_gpl2():
    for op in [' AND ', '<AND>', ' & ', ' && ']:
        __test_impl('mit', op, 'GPLv2', 'MIT AND GPL-2.0-only', ['', ' '])


def _test_or_mit0_gpl2_1():
    __test_impl("mit-0 or GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 || GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 | GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 OR GPLv2", 'MIT-0 OR GPL-2.0-only')
def _test_or_mit0_gpl2_2():
    __test_impl("mit-0 <OR> GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0<OR> GPLv2", 'MIT-0 OR GPL-2.0-only')


