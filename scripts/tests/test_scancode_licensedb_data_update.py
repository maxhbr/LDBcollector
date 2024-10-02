import pytest
import os
import json
from unittest import mock
from src.update.scancode_licensedb_data_update import (
    download_index_json, load_json_file, delete_file, download_license_json,
    get_alias, update_data, add_data, process_licenses
)


# Mock logger to avoid side effects in tests
@pytest.fixture
def mock_logger():
    with mock.patch("src.update.scancode_licensedb_data_update.logger") as logger_mock:
        yield logger_mock


@pytest.fixture
def mock_load_json_file():
    with mock.patch('src.update.scancode_licensedb_data_update.load_json_file') as mock_load_json_file:
        yield mock_load_json_file


@pytest.fixture
def mock_download_license_json():
    with (mock.patch('src.update.scancode_licensedb_data_update.download_license_json')
          as mock_download_license_json_file):
        yield mock_download_license_json_file


@pytest.fixture
def mock_get_alias():
    with mock.patch('src.update.scancode_licensedb_data_update.get_alias') as mock_get_alias:
        yield mock_get_alias


@pytest.fixture
def mock_update_data():
    with mock.patch('src.update.scancode_licensedb_data_update.update_data') as mock_update_data:
        yield mock_update_data


@pytest.fixture
def mock_handle_data():
    with mock.patch('src.update.scancode_licensedb_data_update.handle_data') as mock_handle_data:
        yield mock_handle_data


def test_download_index_json_success(mock_logger):
    url = "https://example.com/index.json"
    output_file = "output.json"

    with mock.patch("src.update.scancode_licensedb_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"{}"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            download_index_json(url, output_file)
            mock_get.assert_called_once_with(url)
            mock_file.assert_called_once_with(output_file, 'wb')
            # noinspection PyArgumentList
            mock_file().write.assert_called_once_with(b"{}")
            mock_logger.debug.assert_called_with("ScanCode index list downloaded successfully.")


def test_download_index_json_failure(mock_logger):
    url = "https://example.com/index.json"
    output_file = "output.json"

    with mock.patch("src.update.scancode_licensedb_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        with mock.patch("builtins.open", mock.mock_open()):
            download_index_json(url, output_file)
            mock_logger.debug.assert_called_with("Failed to download ScanCode index list.")


# Test for load_json_file function
def test_load_json_file(mock_logger):
    filepath = "test.json"
    json_data = {"key": "value"}

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(json_data))):
        result = load_json_file(filepath)
        assert result == json_data
        mock_logger.debug.assert_called_with(f"Load json file from {filepath}")


def test_delete_file_exists(mock_logger):
    filepath = "test.json"

    with mock.patch("os.path.exists", return_value=True), mock.patch("os.remove") as mock_remove:
        delete_file(filepath)
        mock_remove.assert_called_once_with(filepath)
        mock_logger.debug.assert_called_once_with(f"File '{filepath}' deleted successfully.")


def test_delete_file_not_exists(mock_logger):
    filepath = "test.json"

    with mock.patch("os.path.exists", return_value=False), mock.patch("os.remove") as mock_remove:
        delete_file(filepath)
        mock_remove.assert_not_called()
        mock_logger.debug.assert_called_once_with(f"File '{filepath}' does not exist.")


# Test for download_license_json function
def test_download_license_json_success(mock_logger):
    license_key = "mit"
    output_file = "mit.json"
    url = f"https://scancode-licensedb.aboutcode.org/{license_key}.json"

    with mock.patch("src.update.scancode_licensedb_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"{}"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            download_license_json(license_key, output_file)
            mock_get.assert_called_once_with(url)
            mock_file.assert_called_once_with(output_file, 'wb')
            # noinspection PyArgumentList
            mock_file().write.assert_called_once_with(b"{}")
            mock_logger.debug.assert_called_once_with(f"License {license_key}.json downloaded successfully.")


def test_download_license_json_failure(mock_logger):
    license_key = "mit"
    output_file = "mit.json"

    with mock.patch("src.update.scancode_licensedb_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        with mock.patch("builtins.open", mock.mock_open()):
            download_license_json(license_key, output_file)
            mock_logger.debug.assert_called_once_with(f"Failed to download License {license_key}.json")


# Test for get_alias function
def test_get_alias_with_spdx(mock_logger):
    license_data = {
        "key": "mit",
        "short_name": "MIT",
        "name": "MIT License",
        "other_spdx_license_keys": ["mit-alt"]
    }

    alias = get_alias(license_data, is_spdx=True)
    assert set(alias) == {"mit", "MIT", "MIT License", "mit-alt"}


def test_get_alias_without_spdx(mock_logger):
    license_data = {
        "short_name": "MIT",
        "name": "MIT License",
        "key": "mit",
    }

    alias = get_alias(license_data, is_spdx=False)
    assert set(alias) == {"MIT", "MIT License"}


def test_update_data(mock_logger):
    canonical_id = "MIT"
    scancode_aliases = ["mit-alt", "MIT License"]

    data = {
        "canonical": canonical_id,
        "aliases": {
            "scancode-licensedb": [],
            "spdx": []
        }
    }

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))) as mock_file, \
         mock.patch("json.dump") as mock_json_dump:
        update_data(canonical_id, scancode_aliases)

        expected_file_path = os.path.abspath(os.path.join("../../../data", f"{canonical_id}.json"))

        mock_file.assert_any_call(expected_file_path, 'r')

        mock_file.assert_any_call(expected_file_path, 'w')

        mock_json_dump.assert_called_once()


def test_add_data(mock_logger):
    license_key = "MIT"
    aliases = ["mit", "MIT License"]

    output_data = {
        "canonical": license_key,
        "aliases": {
            "scancode-licensedb": aliases,
            "custom": []
        },
        "src": "scancode-licensedb"
    }

    expected_file_path = os.path.abspath(os.path.join("../../../data", f"{license_key}.json"))

    with mock.patch("builtins.open", mock.mock_open()) as mock_file, \
         mock.patch("json.dump") as mock_json_dump:
        add_data(license_key, aliases)
        # Assert that the correct file path is used
        mock_file.assert_called_once_with(expected_file_path, 'w')
        # noinspection PyArgumentList
        mock_json_dump.assert_called_once_with(output_data, mock_file(), indent=4)


def test_license_in_exceptions(mock_logger, mock_load_json_file):
    # Mock data setup: license key in exceptions
    index_data = [{"license_key": "bsd-2-clause-netbsd"}]
    mock_load_json_file.return_value = index_data

    # Call the process_licenses function
    process_licenses()

    # Extract all logger.debug call arguments
    logged_messages = [call.args[0] for call in mock_logger.debug.call_args_list]

    # Verify that the specific "Skipping" message was logged
    assert 'Skipping bsd-2-clause-netbsd' in logged_messages


def test_spdx_license_key(mock_load_json_file, mock_download_license_json, mock_logger,
                          mock_handle_data, mock_update_data, mock_get_alias):
    # Case where spdx_license_key is present and does not start with "LicenseRef"
    index_data = [{"license_key": "some-license"}]
    license_data = {"spdx_license_key": "SPDX-1234"}

    # Mock load_json_file to return index_data and license_data
    mock_load_json_file.side_effect = [index_data, license_data]

    # Call the process_licenses function
    process_licenses()

    # Check if get_alias and update_data are called correctly
    mock_get_alias.assert_called_with(license_data, is_spdx=True)
    mock_update_data.assert_called_with("SPDX-1234", mock_get_alias.return_value)
    mock_handle_data.assert_not_called()

    # Case where spdx_license_key starts with "LicenseRef"
    license_data = {"spdx_license_key": "LicenseRef-1234"}
    mock_load_json_file.side_effect = [index_data, license_data]

    # Call the process_licenses function again
    process_licenses()

    # Check if get_alias and handle_data are called correctly
    mock_get_alias.assert_called_with(license_data, is_spdx=False)
    mock_handle_data.assert_called_with(mock_get_alias.return_value, "some-license")
    # Assert that mock_update_data is only called once
    assert mock_update_data.call_count == 1


def test_no_spdx_license_key(mock_load_json_file, mock_download_license_json, mock_logger,
                             mock_handle_data, mock_get_alias):
    # Case where spdx_license_key is not present
    index_data = [{"license_key": "some-license"}]
    license_data = {}

    # Mock load_json_file to return index_data and license_data
    mock_load_json_file.side_effect = [index_data, license_data]

    # Call the process_licenses function
    process_licenses()

    # Check if get_alias and handle_data are called when no spdx_license_key
    mock_get_alias.assert_called_with(license_data, is_spdx=False)
    mock_handle_data.assert_called_with(mock_get_alias.return_value, "some-license")

    logged_messages = [call.args[0] for call in mock_logger.debug.call_args_list]

    assert 'No SPDX license key found for some-license' in logged_messages


# Test for process_licenses function (integration test)
def test_process_licenses(mock_logger):
    with mock.patch("src.update.scancode_licensedb_data_update.download_index_json"), \
         mock.patch("src.update.scancode_licensedb_data_update.load_json_file",
                    return_value=[{"license_key": "mit"}]), \
         mock.patch("src.update.scancode_licensedb_data_update.download_license_json"), \
         mock.patch("src.update.scancode_licensedb_data_update.get_alias", return_value=["MIT", "MIT License"]), \
         mock.patch("src.update.scancode_licensedb_data_update.update_data"), \
         mock.patch("src.update.scancode_licensedb_data_update.delete_file"):
        process_licenses()
