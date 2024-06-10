# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.license_db import FossLicenses
from flame.license_db import Validation
from flame.exception import FlameException
import logging

fl = FossLicenses(config={
    'duals_file': 'tests/licenses-additional/duals.json',
    'compunds_file': 'tests/licenses-additional/compounds.json',
    'check': True,
    'license-dir': 'tests/licenses',
    'level': 'logging.INFO'})

def test_supported():
    licenses = fl.licenses()
    assert len(licenses) == 6

def test_osadl_validation():
    fl.expression_license("MIT", validations=[Validation.OSADL])
    
    with pytest.raises(FlameException):
        fl.expression_license("MIT2", validations=[Validation.OSADL])
        
    fl.expression_license("GPL-2.0-only WITH Classpath-exception-2.0", validations=[Validation.OSADL])
        
    with pytest.raises(FlameException):
        fl.expression_license("GPL-2.0-only WITH NON_EXIST", validations=[Validation.OSADL])
        
    with pytest.raises(FlameException):
        fl.expression_license("LicenseRef-scancode-unknown-license-reference", validations=[Validation.OSADL])

def test_spdx_validation():
    fl.expression_license("MIT", validations=[Validation.SPDX])
    
    with pytest.raises(FlameException):
        fl.expression_license("MIT2", validations=[Validation.SPDX])

    fl.expression_license("GPL-2.0-only WITH Classpath-exception-2.0", validations=[Validation.SPDX])

    with pytest.raises(FlameException):
        fl.expression_license("GPL-2.0-only WITH NON_EXIST", validations=[Validation.SPDX])

    with pytest.raises(FlameException):
        fl.expression_license("LicenseRef-scancode-unknown-license-reference", validations=[Validation.SPDX])


def test_scancode_validation():
    fl.expression_license("MIT", validations=[Validation.SCANCODE])
    
    with pytest.raises(FlameException):
        fl.expression_license("MIT2", validations=[Validation.SCANCODE])

    fl.expression_license("GPL-2.0-only WITH Classpath-exception-2.0", validations=[Validation.SCANCODE])

    with pytest.raises(FlameException):
        fl.expression_license("GPL-2.0-only WITH NON_EXIST", validations=[Validation.SCANCODE])

    fl.expression_license("LicenseRef-scancode-unknown-license-reference", validations=[Validation.SCANCODE])


def test_scancode_relaxed():
    fl.expression_license("MIT", validations=[Validation.SCANCODE])
    
    fl.expression_license("GPL-2.0-only WITH Classpath-exception-2.0", validations=[Validation.SCANCODE])

    fl.expression_license("LicenseRef-scancode-unknown-license-reference", validations=[Validation.SCANCODE])


