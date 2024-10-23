# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest
import saneyaml

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import cleanup_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_yaml():
    test_dir = test_env.get_test_loc('yaml/simple')
    result_file = test_env.get_temp_file('yaml')
    run_scan_click(['-clip', test_dir, '--yaml', result_file])
    expected = test_env.get_test_loc('yaml/simple-expected.yaml')
    check_yaml_scan(expected, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_does_not_truncate_copyright_yaml():
    test_dir = test_env.get_test_loc('yaml/tree/scan/')
    result_file = test_env.get_temp_file('test.yaml')
    run_scan_click(['-clip', '--strip-root', test_dir, '--yaml', result_file])
    expected = test_env.get_test_loc('yaml/tree/expected.yaml')
    check_yaml_scan(expected, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_for_timestamp():
    test_dir = test_env.get_test_loc('yaml/simple')
    result_file = test_env.get_temp_file('yaml')
    run_scan_click(['-clip', test_dir, '--yaml', result_file])
    result_yaml = saneyaml.load(open(result_file).read())
    header = result_yaml['headers'][0]
    assert 'start_timestamp' in header
    assert 'end_timestamp' in header


def check_yaml_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES):
    """
    Check the scan `result_file` YAML results against the `expected_file`
    expected YAML results.

    If `regen` is True the expected_file WILL BE overwritten with the new scan
    results from `results_file`. This is convenient for updating tests
    expectations. But use with caution.
    """
    results = load_yaml_results(result_file) or {}
    if regen:
        with open(expected_file, 'w') as reg:
            reg.write(saneyaml.dump(results))

    expected = load_yaml_results(expected_file)

    results.pop('headers', None)
    expected.pop('headers', None)

    # NOTE we redump the YAML as a string for a more efficient display of the
    # failures comparison/diff
    expected = saneyaml.dump(expected)
    results = saneyaml.dump(results)
    assert results == expected


def load_yaml_results(location):
    """
    Load the YAML scan results file at `location`.
    To help with test resilience against small changes some attributes are
    removed or streamlined such as the  "tool_version" and scan "errors".
    Also date attributes from "files" and "headers" entries are removed.
    """
    with open(location, encoding='utf-8') as res:
        scan_results = res.read()
    scan_results = saneyaml.load(scan_results)
    return cleanup_scan(scan_results, remove_file_date=True)
