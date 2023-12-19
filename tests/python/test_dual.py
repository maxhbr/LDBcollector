# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import logging

fl = FossLicenses(license_dir="tests/licenses", logging_level=logging.INFO)

def test_no_dual():
    lic = fl.expression_license("GPL-2.0-or-later", update_dual=False)
    assert lic['identified_license'] == "GPL-2.0-or-later"

def test_dual():
    lic = fl.expression_license("GPL-2.0-or-later", update_dual=True)
    assert lic['identified_license'] == "GPL-2.0-only OR GPL-3.0-only"

def test_dual_implicit():
    lic = fl.expression_license("GPL-2.0-or-later")
    assert lic['identified_license'] == "GPL-2.0-only OR GPL-3.0-only"

def test_dual_complex():
    lic = fl.expression_license("GPL-2.0-or-later OR MIT")
    assert lic['identified_license'] == "(GPL-2.0-only OR GPL-3.0-only) OR MIT"

    lic = fl.expression_license("GPL-2.0-or-later AND MIT")
    assert lic['identified_license'] == "(GPL-2.0-only OR GPL-3.0-only) AND MIT"

def test_dual_complexer():
    lic = fl.expression_license("X11 OR GPL-2.0-or-later AND MIT")
    assert lic['identified_license'] == "X11 OR ((GPL-2.0-only OR GPL-3.0-only) AND MIT)"
