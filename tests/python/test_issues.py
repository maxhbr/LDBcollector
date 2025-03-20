#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


import pytest

from flame.license_db import FossLicenses
from flame.exception import FlameException
import logging

fl = FossLicenses(config={
    'duals_file': 'tests/var/duals.json',
    'compounds_file': 'tests/var/compounds.json',
    'check': True,
    'license-dir': 'tests/licenses',
    'level': 'logging.INFO'})

# The tests below make sure that for example "OReilly" isn't treated as "OR eilly". They originate from https://github.com/hesa/foss-licenses/issues/174

def test_174_OReilly():
    for op in ['WITH', 'with', 'w/', 'OR', 'AND']:
        lic = f'MIT {op} OReilly'
        exp_lic = lic.replace('with','WITH').replace('w/', 'WITH')
        c = fl.expression_compatibility_as(lic, update_dual=False)
        assert c['compat_license'] == exp_lic

def test_174_NOReilly():
    for op in ['WITH', 'with', 'w/', 'OR', 'AND']:
        lic = f'MIT {op} NOReilly'
        exp_lic = lic.replace('with','WITH').replace('w/', 'WITH')
        c = fl.expression_compatibility_as(lic, update_dual=False)
        assert c['compat_license'] == exp_lic

def test_174_ANDy():
    for op in ['WITH', 'with', 'w/', 'OR', 'AND']:
        lic = f'MIT {op} ANDy'
        exp_lic = lic.replace('with','WITH').replace('w/', 'WITH')
        c = fl.expression_compatibility_as(lic, update_dual=False)
        assert c['compat_license'] == exp_lic

def test_174_MAND():
    for op in ['WITH', 'with', 'w/', 'OR', 'AND']:
        lic = f'MIT {op} MAND'
        exp_lic = lic.replace('with','WITH').replace('w/', 'WITH')
        c = fl.expression_compatibility_as(lic, update_dual=False)
        assert c['compat_license'] == exp_lic

def test_174_MANDy():
    for op in ['WITH', 'with', 'w/', 'OR', 'AND']:
        lic = f'MIT {op} MANDy'
        exp_lic = lic.replace('with','WITH').replace('w/', 'WITH')
        c = fl.expression_compatibility_as(lic, update_dual=False)
        assert c['compat_license'] == exp_lic

def test_204_and():
    lic = 'mit and GPLv2+'

    exp_lic = 'MIT AND (GPL-2.0-only OR GPL-3.0-only)'
    c = fl.expression_compatibility_as(lic)
    assert c['compat_license'] == exp_lic

    exp_lic = 'MIT AND GPL-2.0-or-later'
    c = fl.expression_compatibility_as(lic, update_dual=False)
    assert c['compat_license'] == exp_lic
    
def test_204_and():
    lic = 'mit and GPLv2+'

    exp_lic = 'MIT AND (GPL-2.0-only OR GPL-3.0-only)'
    c = fl.expression_compatibility_as(lic)
    assert c['compat_license'] == exp_lic

    exp_lic = 'MIT AND GPL-2.0-or-later'
    c = fl.expression_compatibility_as(lic, update_dual=False)
    assert c['compat_license'] == exp_lic
    
def test_204_AND():
    lic = 'mit AND GPLv2+'

    exp_lic = 'MIT AND (GPL-2.0-only OR GPL-3.0-only)'
    c = fl.expression_compatibility_as(lic)
    assert c['compat_license'] == exp_lic

    exp_lic = 'MIT AND GPL-2.0-or-later'
    c = fl.expression_compatibility_as(lic, update_dual=False)
    assert c['compat_license'] == exp_lic
    
def test_204_AMP():
    lic = 'mit & GPLv2+'

    exp_lic = 'MIT AND (GPL-2.0-only OR GPL-3.0-only)'
    c = fl.expression_compatibility_as(lic)
    assert c['compat_license'] == exp_lic

    exp_lic = 'MIT AND GPL-2.0-or-later'
    c = fl.expression_compatibility_as(lic, update_dual=False)
    assert c['compat_license'] == exp_lic
    
def test_204_AMPAMP():
    lic = 'mit && GPLv2+'

    exp_lic = 'MIT AND (GPL-2.0-only OR GPL-3.0-only)'
    c = fl.expression_compatibility_as(lic)
    assert c['compat_license'] == exp_lic

    exp_lic = 'MIT AND GPL-2.0-or-later'
    c = fl.expression_compatibility_as(lic, update_dual=False)
    assert c['compat_license'] == exp_lic
    
