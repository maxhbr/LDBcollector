# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import logging

fl = FossLicenses(config={'license_dir': 'tests/licenses', 'level': 'INFO'})

def test_with_no_dual():
    lic = fl.expression_license("GPL-2.0-or-later WITH Classpath-exception-2.0", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-or-later WITH Classpath-exception-2.0"

def test_with_dual():
    lic = fl.expression_license("GPL-2.0-or-later WITH Classpath-exception-2.0")
    assert lic['identified_license'] == "GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only WITH Classpath-exception-2.0"

def test_with_dual_complex():
    lic = fl.expression_license("MIT OR GPL-2.0-or-later WITH Classpath-exception-2.0")
    assert lic['identified_license'] == "MIT OR (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only WITH Classpath-exception-2.0)"

def test_with_dual_complexer():
    lic = fl.expression_license("MIT OR GPL-2.0-or-later WITH Classpath-exception-2.0 AND BSD-3-Clause")
    assert lic['identified_license'] == "MIT OR ((GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only WITH Classpath-exception-2.0) AND BSD-3-Clause)"
