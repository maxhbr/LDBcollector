import os
import json
import pytest
from unittest import mock
from src.validate.data_validation import (
    download_license_list,
    load_ids_from_license_list,
    delete_file,
    check_json_filename,
    check_unique_aliases,
    check_length_and_characters,
    check_src_and_canonical,
    LicenseListType,
    main
)

# Mock setup_logger to avoid actual logging
mock_logger = mock.MagicMock()


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create the test_data directory before each test
    os.makedirs("test_data", exist_ok=True)
    yield

    # Reset mocks
    mock_logger.reset_mock()

    # Teardown: Remove the test_data directory after each test
    if os.path.exists("test_data"):
        for root, dirs, files in os.walk("test_data", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir("test_data")


def test_download_spdx_license_list():
    url = 'https://example.com/licenses.json'
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = b'{"licenses": []}'

    with mock.patch('requests.get', return_value=mock_response):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            download_license_list(url, filepath, LicenseListType.SPDX)
            mock_logger.info.assert_called_with('LicenseListType.SPDX downloaded successfully.')

            # Check if the file is written
            with open(filepath, 'rb') as f:
                content = f.read()
                assert content == b'{"licenses": []}'


def test_download_spdx_license_list_failure():
    url = 'https://example.com/licenses.json'
    output_file = 'licenses.json'

    mock_response = mock.Mock()
    mock_response.status_code = 404

    with mock.patch('requests.get', return_value=mock_response):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            download_license_list(url, output_file, LicenseListType.SPDX)
            mock_logger.error.assert_called_with("Failed to download LicenseListType.SPDX.")


def test_load_spdx_license_list():
    spdx_data = {"licenses": [{"licenseId": "MIT"}]}
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(spdx_data, f)

    result = load_ids_from_license_list(filepath, LicenseListType.SPDX)
    assert result == ["MIT"]


def test_load_spdx_exception_list():
    spdx_exception_data = {"exceptions": [{"licenseExceptionId": "MIT-Exception"}]}
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(spdx_exception_data, f)

    result = load_ids_from_license_list(filepath, LicenseListType.SPDX_EXCEPTION)
    assert result == ["MIT-Exception"]


def test_load_scancode_licensedb_list_with_spdx_key():
    license_data = [{"spdx_license_key": "MIT-ScanCode"}]
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(license_data, f)

    result = load_ids_from_license_list(filepath, LicenseListType.SCANCODE_LICENSEDB)
    assert result == ["MIT-ScanCode"]


def test_load_scancode_licensedb_list_with_licenseref():
    license_data = [{"spdx_license_key": "LicenseRef-MIT-ScanCode", "license_key": "MIT-ScanCode"}]
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(license_data, f)

    result = load_ids_from_license_list(filepath, LicenseListType.SCANCODE_LICENSEDB)
    assert result == ["MIT-ScanCode"]


def test_load_scancode_licensedb_list_without_spdx_key():
    license_data = [{"license_key": "MIT-ScanCode"}]
    filepath = os.path.join("test_data", 'licenses.json')
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(license_data, f)

    result = load_ids_from_license_list(filepath, LicenseListType.SCANCODE_LICENSEDB)
    assert result == ["MIT-ScanCode"]


def test_delete_file():
    filepath = os.path.join("test_data", "test_file.txt")
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        f.write("test")

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        delete_file(filepath)
        mock_logger.info.assert_called_with(f"File '{filepath}' deleted successfully.")

    assert not os.path.exists(filepath)


def test_delete_file_failure():
    filepath = 'test_file.txt'

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        delete_file(filepath)
        mock_logger.error.assert_called_with(f"File '{filepath}' does not exist.")

    assert not os.path.exists(filepath)


def test_check_json_filename():
    test_data = {"canonical": "correct_name"}
    filepath = os.path.join("test_data", "correct_name.json")
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_json_filename()

    mock_logger.error.assert_not_called()


def test_check_json_filename_failure():
    canonical_name = "correct_name"
    test_data = {"canonical": canonical_name}

    filename = "incorrect_name.json"
    filepath = os.path.join("test_data", filename)
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_json_filename()

    mock_logger.error.assert_called_with(f"JSON filename '{filename}' does not match canonical name '{canonical_name}'")


def dump_files(filepath1, filepath2, test_data1, test_data2):
    with open(filepath1, 'w') as f:
        json.dump(test_data1, f)
    with open(filepath2, 'w') as f:
        json.dump(test_data2, f)


def test_check_unique_aliases():
    test_data1 = {"aliases": {"SPDX": ["alias1", "alias2"]}}
    test_data2 = {"aliases": {"SPDX": ["alias3", "alias4"]}}

    os.makedirs("test_data", exist_ok=True)

    filepath1 = os.path.join("test_data", "file1.json")
    filepath2 = os.path.join("test_data", "file2.json")

    dump_files(filepath1, filepath2, test_data1, test_data2)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_unique_aliases()

    mock_logger.error.assert_not_called()


def test_check_unique_aliases_failure():
    alias_duplicate = "alias1"
    test_data1 = {"aliases": {"SPDX": [alias_duplicate, "alias2"]}}
    test_data2 = {"aliases": {"SPDX": [alias_duplicate, "alias4"]}}

    filenames = ["file1.json", "file2.json"]
    filepath1 = os.path.join("test_data", filenames[0])
    filepath2 = os.path.join("test_data", filenames[1])

    dump_files(filepath1, filepath2, test_data1, test_data2)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_unique_aliases()

    mock_logger.error.assert_called_with(
        f"Alias '{alias_duplicate}' is not unique globally. Affected file: {filenames}")


def test_check_src_and_canonical():
    spdx_licenses = ["MIT", "Apache-2.0"]
    test_data = {"canonical": "MIT", "src": "SPDX"}

    os.makedirs("test_data", exist_ok=True)
    filepath = os.path.join("test_data", "test_file.json")

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_src_and_canonical(spdx_licenses, [], [])

    mock_logger.error.assert_not_called()


def test_check_src_and_canonical_failure():
    spdx_licenses = ["MIT", "Apache-2.0"]
    canonical_name = "NO_SPDX_LICENSE"
    test_data = {"canonical": canonical_name, "src": "SPDX"}

    filepath = os.path.join("test_data", "test_file.json")

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_src_and_canonical(spdx_licenses, [], [])

    mock_logger.error.assert_called_with(
        f"If src is SPDX, canonical name '{canonical_name}' must be in SPDX license list")


def test_check_length_and_characters():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"canonical": "valid_name", "src": "valid_src", "aliases": ["valid_alias", "valid_alias2"]}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with (mock.patch('src.validate.data_validation.DATA_DIR', "test_data")):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_length_and_characters()

    assert mock_logger.error.call_count == 0


def test_check_length_and_characters_failure():
    max_length = 100

    os.makedirs("test_data", exist_ok=True)

    src_too_long = "a" * (max_length + 1)
    long_data = {"canonical": "a" * (max_length + 1), "aliases": ["a" * (max_length + 1)], "src": src_too_long}
    forbidden_data = {"canonical": "invalid#name", "aliases": "alias1", "src": "src"}

    filepath_long = os.path.join("test_data", "long.json")
    filepath_forbidden = os.path.join("test_data", "forbidden.json")

    with open(filepath_long, 'w') as f:
        json.dump(long_data, f)

    with open(filepath_forbidden, 'w') as f:
        json.dump(forbidden_data, f)

    with mock.patch('src.validate.data_validation.DATA_DIR', "test_data"):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            check_length_and_characters()

            # Check for long strings
            mock_logger.error.assert_any_call(f"Canonical name '{long_data['canonical']}' exceeds maximum length "
                                              f"limit of {max_length} characters")

            mock_logger.error.assert_any_call(f"At least one of the aliases exceeds maximum length limit of "
                                              f"{max_length} characters in the file long.json")

            mock_logger.error.assert_any_call(
                f"Source {src_too_long} exceeds maximum length limit of {max_length} characters")

            # Check for forbidden characters
            mock_logger.error.assert_any_call(
                f"Canonical name '{forbidden_data['canonical']}' contains forbidden characters")

    os.remove(filepath_long)
    os.remove(filepath_forbidden)
    os.rmdir("test_data")


def test_main_integration():
    # Mock the logger and its handlers
    mock_logger.handlers = [mock.MagicMock(), mock.MagicMock()]
    mock_logger.handlers[1].error_occurred = False  # Simulate no error occurring

    with mock.patch("src.validate.data_validation.download_license_list"), \
         mock.patch("src.validate.data_validation.load_ids_from_license_list",
                    side_effect=[["license1", "license2"], ["exception1"], ["license3", "license4"]]), \
         mock.patch("src.validate.data_validation.check_src_and_canonical"), \
         mock.patch("src.validate.data_validation.delete_file"), \
         mock.patch("src.validate.data_validation.check_json_filename"), \
         mock.patch("src.validate.data_validation.check_unique_aliases"), \
         mock.patch("src.validate.data_validation.check_length_and_characters"):
        main()

        # Verify that no error occurred (if checking the logger)
        assert not mock_logger.handlers[1].error_occurred, "An error occurred in the logger"


def test_main_integration_fail():
    # Mock the logger and its handlers
    mock_logger.handlers = [mock.MagicMock(), mock.MagicMock()]
    mock_logger.handlers[1].error_occurred = True  # Simulate an error occurring

    with mock.patch("src.validate.data_validation.download_license_list"), \
         mock.patch("src.validate.data_validation.load_ids_from_license_list",
                    side_effect=[["license1", "license2"], ["exception1"], ["license3", "license4"]]), \
         mock.patch("src.validate.data_validation.check_src_and_canonical"), \
         mock.patch("src.validate.data_validation.delete_file"), \
         mock.patch("src.validate.data_validation.check_json_filename"), \
         mock.patch("src.validate.data_validation.check_unique_aliases"), \
         mock.patch("src.validate.data_validation.check_length_and_characters"):
        main()

        # Verify that no error occurred (if checking the logger)
        assert mock_logger.handlers[1].error_occurred, "An error occurred in the logger"


if __name__ == "__main__":
    pytest.main()
