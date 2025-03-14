#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
from unittest.mock import MagicMock, patch
import pytest
from src.update.ScancodeLicensedbDataUpdate import ScancodeLicensedbDataUpdate


# Test for get_aliases function
def test_get_alias_with_spdx(capsys):
    license_data = {
        "key": "mit",
        "short_name": "MIT",
        "name": "MIT License",
        "other_spdx_license_keys": ["mit-alt", "mit-license"]
    }
    scancode_licensedb_data_update = ScancodeLicensedbDataUpdate()

    alias = scancode_licensedb_data_update.get_aliases(license_data, is_spdx=True)
    assert set(alias) == {"mit", "MIT", "MIT License", "mit-alt", "mit-license"}


def test_get_alias_without_spdx(capsys):
    license_data = {
        "short_name": "MIT",
        "name": "MIT License",
        "key": "mit",
    }
    scancode_licensedb_data_update = ScancodeLicensedbDataUpdate()

    alias = scancode_licensedb_data_update.get_aliases(license_data, is_spdx=False)
    assert set(alias) == {"MIT", "MIT License"}


@pytest.fixture
def scancode_licensedb_update():
    """
    Fixture to initialize an instance of ScancodeLicensedbDataUpdate with a mock DATA_DIR.
    """
    class_instance = ScancodeLicensedbDataUpdate()
    class_instance._DATA_DIR = "/mock/data/dir"
    class_instance._EXCEPTION_SCANCODE_LICENSEDB = {"exception_license"}
    class_instance._LOGGER = MagicMock()  # Mock logger to suppress actual logging
    return class_instance


def test_process_license(scancode_licensedb_update, capsys):
    mock_license_list = [
        {
            "license_key": "3com-microcode",
            "spdx_license_key": "LicenseRef-scancode-3com-microcode",
            "other_spdx_license_keys": [],
            "json": "3com-microcode.json",
        },
        {
            "license_key": "lgpl-2.0",
            "spdx_license_key": "LGPL-2.0-only",
            "other_spdx_license_keys": [
                "LGPL-2.0",
                "LicenseRef-LGPL-2",
                "LicenseRef-LGPL-2.0"
            ]
        },
        {
            "license_key": "lgpl-200",
            "other_spdx_license_keys": [
                "LGPL-200.0",
                "LicenseRef-LGPL-200",
                "LicenseRef-LGPL-200.0"
            ]
        }
    ]

    mock_license_licenseref = {
        "key": "3com-microcode",
        "short_name": "3Com Microcode",
        "name": "3Com Microcode",
        "spdx_license_key": "LicenseRef-scancode-3com-microcode"
    }

    mock_license_spdx = {
        "key": "lgpl-2.0",
        "short_name": "LGPL 2.0",
        "name": "GNU Library General Public License 2.0",
        "spdx_license_key": "LGPL-2.0-only",
        "other_spdx_license_keys": [
            "LGPL-2.0",
            "LicenseRef-LGPL-2",
            "LicenseRef-LGPL-2.0"
        ]
    }

    mock_license_no_spdx = {
        "key": "lgpl-200",
        "short_name": "LGPL 200.0",
        "name": "GNU Library General Public License 200.0",
    }
    scancode_licensedb_update.download_json_file = MagicMock()
    scancode_licensedb_update.load_json_file = MagicMock(
        side_effect=[mock_license_list, mock_license_licenseref, mock_license_spdx, mock_license_no_spdx])
    scancode_licensedb_update.update_license_file = MagicMock()
    scancode_licensedb_update.create_license_file = MagicMock()
    scancode_licensedb_update.handle_data = MagicMock()
    scancode_licensedb_update.delete_file = MagicMock()

    scancode_licensedb_update.process_licenses()

    assert scancode_licensedb_update.download_json_file.call_count == 4
    assert scancode_licensedb_update.load_json_file.call_count == 4
    assert scancode_licensedb_update.handle_data.call_count == 2
    assert scancode_licensedb_update.delete_file.call_count == 4

    scancode_licensedb_update._LOGGER.debug.assert_any_call("Starts with 'LicenseRef' as SPDX key")
    scancode_licensedb_update._LOGGER.debug.assert_any_call("No other spdx license keys for 3com-microcode")
    scancode_licensedb_update._LOGGER.debug.assert_any_call("lgpl-2.0 is already a spdx license")
    scancode_licensedb_update._LOGGER.debug.assert_any_call("No SPDX license key found for lgpl-200")

    assert scancode_licensedb_update._LOGGER.debug.call_count == 5


@patch("os.path.exists")
def test_handle_data_update(mock_exists, scancode_licensedb_update):
    """
    Test the case where the license file already exists.
    """

    # Mock class methods
    scancode_licensedb_update.update_license_file = MagicMock()
    scancode_licensedb_update.create_license_file = MagicMock()

    # Mock os.path.exists to return True
    mock_exists.return_value = True

    # Define input arguments
    aliases = ["Alias1", "Alias2"]
    license_key = "test_license"

    # Call the method under test
    scancode_licensedb_update.handle_data(aliases, license_key)

    # Assert that update_license_file was called with the correct arguments
    scancode_licensedb_update.update_license_file.assert_called_once_with(license_key, aliases)

    # Assert that create_license_file was NOT called
    scancode_licensedb_update.create_license_file.assert_not_called()


@patch("os.path.exists")
def test_handle_data_create(mock_exists, scancode_licensedb_update):
    """
    Test the case where the license file does not exist.
    """
    instance = scancode_licensedb_update

    # Mock class methods
    instance.update_license_file = MagicMock()
    instance.create_license_file = MagicMock()
    instance.get_file_for_unrecognized_id = MagicMock(side_effect=[None])

    # Mock os.path.exists to return False
    mock_exists.return_value = False

    # Define input arguments
    aliases = ["Alias1", "Alias2"]
    license_key = "test_license"

    # Call the method under test
    instance.handle_data(aliases, license_key)

    # Assert that create_license_file was called with the correct arguments
    instance.create_license_file.assert_called_once_with(license_key, aliases)

    # Assert that update_license_file was NOT called
    instance.update_license_file.assert_not_called()


@patch("os.path.exists")
def test_handle_data_not_create(mock_exists, scancode_licensedb_update):
    """
    Test the case where the license file does not exist.
    """
    instance = scancode_licensedb_update

    # Mock class methods
    instance.update_license_file = MagicMock()
    instance.create_license_file = MagicMock()
    instance.get_file_for_unrecognized_id = MagicMock(side_effect=["test_license"])

    # Mock os.path.exists to return False
    mock_exists.return_value = False

    # Define input arguments
    aliases = ["Alias1", "Alias2"]
    license_key = "test_license"

    # Call the method under test
    instance.handle_data(aliases, license_key)

    # Assert that create_license_file was called with the correct arguments
    instance.create_license_file.assert_not_called()

    # Assert that update_license_file was NOT called
    instance.update_license_file.assert_not_called()
