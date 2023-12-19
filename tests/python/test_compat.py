# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.license_db import FossLicenses
from flame.license_db import Validation
from flame.exception import FlameException
import logging

fl = FossLicenses(license_dir="tests/licenses", logging_level=logging.INFO)

def test_compat_misc_blanks():
    # add misc blanks to the license expression
    for i in range(1, 10):
        for j in range(1, 10):
            for k in range(1, 10):
                c = fl.expression_compatibility_as(f'{" "*i}GPLv2+{" "*j}&& BSD3{" "*k}', update_dual=False)
                assert c['compat_license'] == "GPL-2.0-or-later AND BSD-3-Clause"

def compat_misc_paranthesises_sub(lic1, op, lic2, expected):
    for i in range(1, 3):
        for j in range(1, 3):
            for k in range(1, 3):
                for l in range(1, 3):
                    for m in range(1, 3):
                        c = fl.expression_compatibility_as(f'{" "*i}({" "*j}{lic1}{" "*k}{op}{" "*l}{lic2}{" "*m})', update_dual=False)
                        assert c['compat_license'] == expected

def test_compat_misc_paranthesises():
    for op in ['&', '&&', 'and', 'AND']:
        compat_misc_paranthesises_sub('GPLv2+', op, 'bsd-new', 'GPL-2.0-or-later AND BSD-3-Clause')

    for op in ['|', '||', 'or', 'OR']:
        compat_misc_paranthesises_sub('GPLv2+', op, 'bsd-new', 'GPL-2.0-or-later OR BSD-3-Clause')

def test_compat_validations():

    c = fl.expression_compatibility_as('No no license')
    assert c['compat_license'] == 'LicenseRef-dummy-no-compat'

    c = fl.expression_compatibility_as('No no license', [Validation.RELAXED], update_dual=False)
    assert c['compat_license'] == "LicenseRef-dummy-no-compat"

    with pytest.raises(FlameException):
        c = fl.expression_compatibility_as('No no license', [Validation.SPDX], update_dual=False)

    with pytest.raises(FlameException):
        c = fl.expression_compatibility_as('No no license', [Validation.OSADL], update_dual=False)
