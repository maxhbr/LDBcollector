# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import os
import flame.exception

SW_VERSION = '0.19.13'

PYTHON_DIR = os.path.dirname(os.path.realpath(__file__))
VAR_DIR = os.path.join(PYTHON_DIR, 'var')
LICENSE_DIR = os.path.join(VAR_DIR, 'licenses')

LICENSE_SCHEMA_FILE = os.path.join(VAR_DIR, 'license_schema.json')
LICENSE_OPERATORS_FILE = os.path.join(VAR_DIR, 'operators.json')
LICENSE_COMPUNDS_FILE = os.path.join(VAR_DIR, 'compounds.json')
LICENSE_AMBIG_FILE = os.path.join(VAR_DIR, 'ambiguities.json')
LICENSE_DUALS_FILE = os.path.join(VAR_DIR, 'duals.json')

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

def __read_config_helper(path):
    logging.debug(f'try reading: {path}')
    try:
        with open(path) as fp:
            logging.debug('data found')
            return json.load(fp)
    except Exception as e:
        logging.debug(f'file not found or usable: {path}')
        logging.debug(f'exception: {e}')
    raise flame.exception.FlameException(f'Could not read file: {path}')

def read_config(config_file=None):
    logging.debug('reading config')
    for path in [
            config_file,
            os.environ.get('FLAME_USER_CONFIG', None),
    ]:
        logging.debug(f'reading {path}')
        if path:
            try:
                return __read_config_helper(path)
            except Exception as e:
                logging.debug(f'reading {path} failed with {e}')
                raise flame.exception.FlameException(f'Could not read user specified file: {path}')

    for path in [
            os.path.join(os.environ.get('HOME', '/does/not/exist'), '.floss-flame.cfg'),
    ]:
        logging.debug(f'reading {path}')
        try:
            return __read_config_helper(config_file)
        except Exception as e:
            logging.debug(f'reading {path} failed with {e}')
            pass
    return {}
