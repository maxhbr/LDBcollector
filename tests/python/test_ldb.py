#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import sys
import pytest

from flame.license_db import LicenseDatabase
from flame.exception import LicenseDatabaseError
import logging

ldb = LicenseDatabase(check=True, license_dir="tests/licenses", logging_level=logging.INFO)
        
def test_alias_list():

    # list of all aliases
    aliases = ldb.aliases_list()
    assert len(aliases) == 4

def test_aliases():

    # list of all aliases for GPL-2.0-or-later
    aliases = ldb.aliases("GPL-2.0-or-later")
    aliases.sort()
    assert aliases == [ "GPL2+",  "GPLv2+" ]

def test_aliases_bad_input():

    # make sure bad input raises exception
    with pytest.raises(LicenseDatabaseError) as _error:
        ldb.aliases(None)

    with pytest.raises(LicenseDatabaseError) as _error:
        ldb.aliases("Dummy")



def test_compat_as_list():

    c = ldb.compatibility_as_list()
    assert len(c) == 1

def test_compat_as():

    c = ldb.compatibility_as("GPL-2.0-or-later")
    assert c['compatibility_as'] == "GPL-2.0-or-later"
        
def test_compat_as_aliased():

    c = ldb.compatibility_as("GPLv2+")
    assert c['compatibility_as'] == "GPL-2.0-or-later"
        
def test_compat_as_bad_input():

    with pytest.raises(LicenseDatabaseError) as _error:
        ldb.compatibility_as(None)

    with pytest.raises(LicenseDatabaseError) as _error:
        ldb.compatibility_as("Not existing")

