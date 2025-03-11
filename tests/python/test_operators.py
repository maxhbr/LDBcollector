# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.license_db import FossLicenses
from flame.exception import FlameException
import logging

fl = FossLicenses(config={
    'level': 'logging.INFO'})

logger = logging.getLogger("test_values")
logging.basicConfig(encoding='utf-8', level=logging.INFO)

def __test_impl(lic_expr, expected_lic):
    lic = fl.expression_license(lic_expr, update_dual=False)
    logging.debug(f'assert {lic["identified_license"]} == {expected_lic}')
    assert lic['identified_license'] == expected_lic
    

def test_and_mit_gpl2_1():
    __test_impl("mit and GPLv2", 'MIT AND GPL-2.0-only')
    __test_impl("mit && GPLv2", 'MIT AND GPL-2.0-only')
    __test_impl("mit & GPLv2", 'MIT AND GPL-2.0-only')
    __test_impl("mit AND GPLv2", 'MIT AND GPL-2.0-only')

def test_or_mit0_gpl2_1():
    __test_impl("mit-0 or GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 || GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 | GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0 OR GPLv2", 'MIT-0 OR GPL-2.0-only')
def test_or_mit0_gpl2_2():
    __test_impl("mit-0 <OR> GPLv2", 'MIT-0 OR GPL-2.0-only')
    __test_impl("mit-0<OR> GPLv2", 'MIT-0 OR GPL-2.0-only')


