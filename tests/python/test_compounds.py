# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import logging

fl = FossLicenses(license_dir="tests/licenses", logging_level=logging.INFO)

def test_compound_gpl_with():
    lic = fl.expression_license("GPL-2.0-with-classpath-exception", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-only WITH Classpath-exception-2.0"

def test_compound_gpl_with_bad():
    lic = fl.expression_license("GPL-2.0-with-ERROR-classpath-exception", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-with-ERROR-classpath-exception"

def test_compound_gpl_with_and():
    lic = fl.expression_license("GPL-2.0-only AND Classpath-exception-2.0", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-only WITH Classpath-exception-2.0"
