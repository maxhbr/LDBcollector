# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flame.license_db import FossLicenses
import flame.config
import logging
import os

def test_no_config_read():
    # verify no config is read
    config = flame.config.read_config()
    assert config.get('additional-license-dir', '--') == '--'

def test_config_read():
    # verify config *is* read
    # add additional dirs (with licenses) using environment variable
    os.environ['FLAME_USER_CONFIG'] = 'tests/user.json'
    config = flame.config.read_config()
    assert config.get('additional-license-dir') == './tests/additional-licenses/'
