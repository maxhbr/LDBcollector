# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.license_db import FossLicenses
from flame.exception import FlameException
import logging

fl = FossLicenses(config={
    'duals_file': 'tests/var/duals.json',
    'compounds_file': 'tests/var/compounds.json',
    'check': True,
    'license-dir': 'tests/licenses',
    'level': 'logging.INFO'})

def test_supported():
    licenses = fl.licenses()
    assert len(licenses) == 6

def test_alias_list():
    # list of all aliases
    aliases = fl.alias_list()
    assert len(aliases) == 11

def test_alias_list_gpl():
    # list of all aliases with license with GPL
    aliases = fl.alias_list("GPL")
    assert len(aliases) == 7

def test_aliases():
    # list of all aliases for GPL-2.0-or-later
    aliases = fl.aliases("GPL-2.0-or-later")
    aliases.sort()
    assert aliases == ["GNU General Public License v2 or later (GPLv2+)", "GPL (v2 or later)", "GPL2+", "GPLv2+"]

def test_aliases_bad_input():
    # make sure bad input raises exception
    with pytest.raises(FlameException):
        fl.aliases(None)

    with pytest.raises(FlameException):
        fl.aliases("Dummy")

def test_expression_license():
    lic = fl.expression_license("GPL2+", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-or-later"

    lic = fl.expression_license("GPL (v2 or later)", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-or-later"

    lic = fl.expression_license("BSD-3-Clause and BSD3", update_dual=False)
    assert lic['identified_license'] == "BSD-3-Clause AND BSD-3-Clause"

def test_with_license_1():
    lic = fl.expression_license("BSD-3-Clause WITH SomeException", update_dual=False)
    assert lic['identified_license'] == "BSD-3-Clause WITH SomeException"

def test_with_license_2():
    lic = fl.expression_license("BSD3 w/SomeException", update_dual=False)
    assert lic['identified_license'] == "BSD-3-Clause WITH SomeException"

def test_with_license_with_parent():
    """Test issue 69"""
    lic = fl.expression_license("GNU General Public License v2 or later (GPLv2+)", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-or-later"
    pass

def test_expression_license_types():
    lic = fl.expression_license("BSD-3-Clause and BSD3", False)
    assert 'queried_license' in lic
    assert isinstance(lic['queried_license'], str)

    assert 'identified_license' in lic
    assert isinstance(lic['identified_license'], str)

    assert 'identifications' in lic
    assert isinstance(lic['identifications'], list)

def test_fail_expression_license():
    with pytest.raises(FlameException):
        fl.expression_license(None)

    with pytest.raises(FlameException):
        fl.expression_license([])

    with pytest.raises(FlameException):
        fl.expression_license(Exception())

def test_compat_as_list():
    c = fl.compatibility_as_list()
    assert len(c) == 1

def test_compat_as():
    c = fl.expression_compatibility_as("GPL-2.0-or-later", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later"

def test_compat_as_aliased():
    c = fl.expression_compatibility_as("GPLv2+", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later"

    c = fl.expression_compatibility_as("GPLv2+ | BSD3", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"

    c = fl.expression_compatibility_as("GPLv2+ || BSD3", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"

    c = fl.expression_compatibility_as("GPLv2+ & BSD3", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"

    c = fl.expression_compatibility_as("GPLv2+ && BSD3", update_dual=False)
    assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"

def test_operator_op():
    for op in ["|", "||", "or", "OR"]:
        c = fl.expression_compatibility_as(f'GPLv2+ {op} BSD3', update_dual=False)
        assert c['compat_license'] == "GPL-2.0-or-later OR BSD-3-Clause"

def test_operator_and():
    for op in ["&", "&&", "and", "AND"]:
        c = fl.expression_compatibility_as(f'GPLv2+ {op} BSD3', update_dual=False)
        assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"

def test_operator_with():
    for op in ["WITH", "with", "w/"]:
        # add misc blanks to the license expression
        for i in range(1, 10):
            c = fl.expression_compatibility_as(f'GPLv2+ {op}{" "*i}Exception', update_dual=False)
            assert c['compat_license'] == "GPL-2.0-or-later WITH Exception"

def test_operators():
    operators = fl.operators()
    assert len(operators) > 3

def _do_nada_test_compat_as_bad_input():

    with pytest.raises(FlameException):
        fl.expression_compatibility_as(None)

    with pytest.raises(FlameException):
        fl.expression_compatibility_as("Not existing")

