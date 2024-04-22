# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import logging

# add additional dirs (with licenses)
fl = FossLicenses(config={
    'license-dir': 'tests/licenses',
    'duals_file': 'tests/licenses-additional/duals.json',
    'compunds_file': 'tests/licenses-additional/compounds.json',
    'level': 'INFO',
    'additional-license-dir': 'tests/additional-licenses'})

# standard (default licenses)
fl_std = FossLicenses(config={'license-dir': 'tests/licenses', 'level': 'INFO'})


def test_mylicense_present():
    """Make sure license in additional dir is present in extended but not
    in standard
    """
    assert 'LicenseRef-mycompany-mylicense' in fl.licenses()
    assert 'LicenseRef-mycompany-mylicense' not in fl_std.licenses()

def test_mylicense_compat():
    """Make sure license compat in additional dir is present in extended
    but not in standard
    """
    c = fl.expression_compatibility_as('LicenseRef-mycompany-mylicense')
    assert c['compat_license'] == 'MIT'

    c = fl_std.expression_compatibility_as('LicenseRef-mycompany-mylicense')
    assert c['compat_license'] == 'LicenseRef-mycompany-mylicense'
    
