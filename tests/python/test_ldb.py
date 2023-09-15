#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import sys
import pytest

from flame.license_db import FossLicenses
from flame.exception import FlameException
import logging

fl = FossLicenses(check=True, license_dir="tests/licenses", logging_level=logging.INFO)
        
def test_alias_list():
    # list of all aliases
    aliases = fl.aliases_list()
    assert len(aliases) == 5

def test_alias_list_gpl():
    # list of all aliases with license with GPL
    aliases = fl.aliases_list("GPL")
    assert len(aliases) == 3

def test_aliases():
    # list of all aliases for GPL-2.0-or-later
    aliases = fl.aliases("GPL-2.0-or-later")
    aliases.sort()
    assert aliases == [ "GPL (v2 or later)", "GPL2+",  "GPLv2+" ]

def test_aliases_bad_input():
    # make sure bad input raises exception
    with pytest.raises(FlameException) as _error:
        fl.aliases(None)

    with pytest.raises(FlameException) as _error:
        fl.aliases("Dummy")

def test_expression_license():
    lic = fl.expression_license("GPL2+")
    print("lic: " + str(lic), file=sys.stderr)
    assert lic['identified_license'] == "GPL-2.0-or-later"

def test_expression_license_with_blank():
    lic = fl.expression_license("GPL (v2 or later)")
    assert lic['identified_license'] == "GPL-2.0-or-later"

def test_expression_license():
    lic = fl.expression_license("BSD-3-Clause and BSD3")
    assert lic['identified_license'] == "BSD-3-Clause AND BSD-3-Clause"

def test_with_license_1():
    lic = fl.expression_license("BSD-3-Clause WITH SomeException")
    assert lic['identified_license'] == "BSD-3-Clause WITH SomeException"

def test_with_license_2():
    lic = fl.expression_license("BSD3 w/SomeException")
    assert lic['identified_license'] == "BSD-3-Clause WITH SomeException"

def test_with_license_3():
    lic = fl.expression_license("BSD3 with SomeException")
    assert lic['identified_license'] == "BSD-3-Clause WITH SomeException"

def test_expression_license_types():
    lic = fl.expression_license("BSD-3-Clause and BSD3")
    assert 'queried_license' in lic
    assert isinstance(lic['queried_license'], str)

    assert 'identified_license' in lic
    assert isinstance(lic['identified_license'], str)

    assert 'identifications' in lic
    assert isinstance(lic['identifications'], list)

def test_fail_expression_license():
    with pytest.raises(FlameException) as _error:
        fl.expression_license(None)

    with pytest.raises(FlameException) as _error:
        fl.expression_license([])

    with pytest.raises(FlameException) as _error:
        fl.expression_license(Exception())

def test_compat_as_list():
    c = fl.compatibility_as_list()
    assert len(c) == 1

def test_compat_as():
    c = fl.expression_compatibility_as("GPL-2.0-or-later")
    assert c['compat_license'] == "GPL-2.0-or-later"
        
def test_compat_as_aliased():
    c = fl.expression_compatibility_as("GPLv2+")
    assert c['compat_license'] == "GPL-2.0-or-later"
        
def test_compat_as_aliased():
    c = fl.expression_compatibility_as("GPLv2+ | BSD3")
    assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"
        
    c = fl.expression_compatibility_as("GPLv2+ || BSD3")
    assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"
        
    c = fl.expression_compatibility_as("GPLv2+ & BSD3")
    assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"
        
    c = fl.expression_compatibility_as("GPLv2+ && BSD3")
    assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"


def test_operator_op():
    for op in [ "|", "||", "or", "OR" ]:
        c = fl.expression_compatibility_as(f'GPLv2+ {op} BSD3')
        assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"

def test_operator_and():
    for op in [ "&", "&&", "and", "AND" ]:
        c = fl.expression_compatibility_as(f'GPLv2+ {op} BSD3')
        assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"

def test_operator_with():
    for op in [ "WITH", "with", "w/" ]:
        # add misc blanks to the license expression
        for i in range(1,10):
            c = fl.expression_compatibility_as(f'GPLv2+ {op}{" "*i}Exception')
            assert c['compat_license'] == "GPL-2.0-or-later WITH Exception"

def test_operators():
    operators = fl.operators()
    assert len(operators) > 3

def _do_nada_test_compat_as_bad_input():

    with pytest.raises(FlameException) as _error:
        fl.expression_compatibility_as(None)

    with pytest.raises(FlameException) as _error:
        fl.expression_compatibility_as("Not existing")
