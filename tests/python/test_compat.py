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

def test_compat_misc_blanks():
    # add misc blanks to the license expression
    for i in range(1,10):
        for j in range(1,10):
            for k in range(1,10):
                c = fl.expression_compatibility_as(f'{" "*i}GPLv2+{" "*j}&& BSD3{" "*k}')
                assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"


def compat_misc_paranthesises_sub(lic1, op, lic2, expected):
    for i in range(1,3):
        for j in range(1,3):
            for k in range(1,3):
                for l in range(1,3):
                    for m in range(1,3):
                        c = fl.expression_compatibility_as(f'{" "*i}({" "*j}{lic1}{" "*k}{op}{" "*l}{lic2}{" "*m})')
                        assert c['compat_license'] == expected
            
def test_compat_misc_paranthesises():
    for op in [ '&', '&&', 'and', 'AND' ]:
        compat_misc_paranthesises_sub('GPLv2+', op, 'bsd-new', 'GPL-2.0-or-later AND BSD-3-Clause')

    for op in [ '|', '||', 'or', 'OR' ]:
        compat_misc_paranthesises_sub('GPLv2+', op, 'bsd-new', 'GPL-2.0-or-later OR BSD-3-Clause')

