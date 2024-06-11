# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flame.exception import FlameException
from flame.license_db import FossLicenses, Validation
import logging

fl_default = FossLicenses(config={
    'duals_file': 'tests/var/duals.json',
    'compounds_file': 'tests/var/compounds.json',
    'check': True,
    'license-dir': 'tests/licenses',
    'level': 'logging.INFO'})
fl_matrix = FossLicenses(config={
    'duals_file': 'tests/var/duals.json',
    'compounds_file': 'tests/var/compounds.json',
    'check': True,
    'license-dir': 'tests/licenses',
    'level': 'logging.INFO',
    'license-matrix-file': 'tests/mini-matrix.json'})

def test_licenses():
    licenses = fl_default.licenses()
    assert len(licenses) == 6

def test_compat_default():
    compat = fl_default.expression_compatibility_as("MIT")
    assert compat['compat_license'] == 'MIT'

def test_compat_matrix_mit():
    compat = fl_default.expression_compatibility_as("MIT", validations=[Validation.OSADL])
    assert compat['compat_license'] == 'MIT'

def test_compat_matrix_unknown():
    compat = fl_default.expression_compatibility_as("unknown")
    assert compat['compat_license'] == 'unknown'

def test_compat_matrix_unknown_validate():
    with pytest.raises(FlameException):
        compat = fl_default.expression_compatibility_as("unknown", validations=[Validation.OSADL])

