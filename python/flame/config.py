# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import os

SW_VERSION = "0.1.8"

PYTHON_DIR = os.path.dirname(os.path.realpath(__file__))
VAR_DIR = os.path.join(PYTHON_DIR, 'var')
LICENSE_DIR = os.path.join(VAR_DIR, 'licenses')

LICENSE_SCHEMA_FILE = os.path.join(VAR_DIR, 'license_schema.json')
LICENSE_OPERATORS_FILE = os.path.join(VAR_DIR, 'operators.json')

DESCRIPTION = """
NAME
  flame (FOSS License Additional Metadata) is a python API and
  command line tool

DESCRIPTION
  FOSS Licenses is a database with additional metadata about, primarily, FOSS licenses.

"""

EPILOG = f"""
CONFIGURATION
  All config files can be found in
  {VAR_DIR}

AUTHOR
  Henrik Sandklef

PROJECT SITE
  https://github.com/hesa/flame

REPORTING BUGS
  File a ticket at https://github.com/hesa/flame/issues

COPYRIGHT
  Copyright (c) 2023 Henrik Sandklef<hesa@sandklef.com>.
  License GPL-3.0-or-later

ATTRIBUTION
"""

def read_config():
    for path in [
        os.environ.get('FLAME_USER_CONFIG'),
        os.path.join(os.environ.get('HOME', '/does/not/exist'), '.floss-flame.cfg'),
    ]:
        logging.debug("try reading: " + str(path))
        try:
            with open(path) as fp:
                logging.debug("data found: ")
                return json.load(fp)
        except Exception as e:
            logging.debug("file not found: ")
            logging.debug(str(e))
            pass
    return {}
