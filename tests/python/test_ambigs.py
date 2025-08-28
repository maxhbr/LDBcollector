# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import logging

fl = FossLicenses(config={
    'license-dir': 'tests/licenses',
    'level': 'INFO',
    'duals_file': 'tests/var/duals.json',
    'compounds_file': 'tests/var/compounds.json'
})

def test_ambig_gpl():
    lic = fl.expression_license("GPL", update_dual=False)
    assert lic['identified_license'] == "GPL"
    assert lic['ambiguities']
    assert len(lic['ambiguities']) == 1

def test_no_ambig_gpl():
    lic = fl.expression_license("GPL-2.0-only", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-only"
    assert not lic['ambiguities']


