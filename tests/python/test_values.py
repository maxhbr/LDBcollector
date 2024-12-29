#!/bin/env python3

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


#
# This file makes sure that
# * each files aliases point to the correct license
# * each (unique) alias points to the correct license
# * each (unique) compound/ambig/compat/operator points to the correct license
# * 
#
#


import json
import logging
import sys
from flame.license_db import FossLicenses
import flame.exception
import license_expression

logger = logging.getLogger("test_values")
logging.basicConfig(encoding='utf-8', level=logging.INFO)

fl = FossLicenses()

tot_count = 0

def test_licenses():
    count = 0
    for lic in fl.licenses():
        lic_obj = fl.license_complete(lic)
        logging.debug(f'{lic}:')
        for alias in lic_obj['aliases']:
            logging.debug(f'    {alias}')
            expression = fl.expression_license(alias, update_dual=False)
            assert lic == expression['identified_license']
            count += 1
    global tot_count
    tot_count += count
    logging.info(f'aliases tested: {count} (via licenses())')

def test_aliases():
    count = 0
    for alias, lic in fl.alias_list().items():
        logging.debug(f'{lic}:')
        expression = fl.expression_license(alias, update_dual=False)
        assert lic == expression['identified_license']
        count += 1
    global tot_count
    tot_count += count
    logging.info(f'aliases tested: {count} (via alias_list()')

def test_compounds():
    count = 0
    for compound in fl.compound_list():
        compound_spdx = compound['spdxid']
        logging.debug("compound: " + compound_spdx)
        for alias in compound['aliases']:
            logging.debug(f'  alias: {alias}')
            expression = fl.expression_license(alias, update_dual=False)
            assert compound_spdx == expression['identified_license']
            count += 1
    global tot_count
    tot_count += count
    logging.info(f'compounds tested: {count}')
            
def test_ambigs():
    count = 0
    for k, v in fl.ambiguities_list().items():
        logging.debug("ambig: " + k)
        for alias in v['aliases']:
            logging.debug(f'  alias: {alias}')
            # we can get an exception (if the expression has weird "(" ")" that fails parsing)
            try:
                expression = fl.expression_license(alias, update_dual=False)
                assert expression['ambiguities'][0]['ambigous_license'] == k
            except flame.exception.FlameException as e:
                # flamexception thrown 
                logging.debug("e: " + str(type(e)))
                logging.debug("e: " + str(e))
            except license_expression.ExpressionError as e:
                # if parsing failed 
                logging.debug("e: " + str(type(e)))
                logging.debug("e: " + str(e))
            count += 1
    global tot_count
    tot_count += count
    logging.info(f'ambigs tested: {count}')
            
def test_compats():
    count = 0
    for compat in fl.compatibility_as_list():
        compat_as = compat['compatibility_as']
        lic = compat['spdxid']

        expression = fl.expression_compatibility_as(lic, update_dual=False)
        assert expression['compat_license'] == compat_as

        count += 1
        
    global tot_count
    tot_count += count
    logging.info(f'compat as tested: {count}')
            

def test_operators():
    count = 0
    for compat_as, lic in fl.operators().items():
        test_expression = f'MIT {compat_as} BSD-3-Clause'
        expected_expression = f'MIT {lic} BSD-3-Clause'
        expression = fl.expression_license(test_expression, update_dual=False)
        assert expression['identified_license'] == expected_expression

        count += 1
        
    global tot_count
    tot_count += count
    logging.info(f'compat as tested: {count}')
            

test_licenses()
test_aliases()
test_compounds()
test_ambigs()
test_compats()
test_operators()
print("total count: " + str(tot_count))
