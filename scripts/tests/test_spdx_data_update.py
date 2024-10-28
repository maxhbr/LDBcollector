import pytest
import os
import json
from unittest import mock
from src.update.spdx_data_update import (download_spdx_license_list, load_spdx_license_list, delete_file,
                                         remove_duplicate_licenses, collect_duplicates, check_canonical_name_with_file,
                                         build_canonical_dictionary, is_spdx_source, DATA_DIR, process_json)


# Mock logger to avoid side effects in tests
@pytest.fixture
def mock_logger():
    with mock.patch("src.update.spdx_data_update.logger") as logger_mock:
        yield logger_mock


# Test for download_spdx_license_list
def test_download_spdx_license_list_success(mock_logger):
    url = "https://example.com/licenses.json"
    output_file = "output.json"

    with mock.patch("src.update.spdx_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"{}"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            download_spdx_license_list(url, output_file)
            mock_get.assert_called_once_with(url)
            mock_file.assert_called_once_with(output_file, 'wb')
            # noinspection PyArgumentList
            mock_file().write.assert_called_once_with(b"{}")
            mock_logger.debug.assert_called_with("SPDX license list downloaded successfully.")


def test_download_spdx_license_list_fail(mock_logger):
    url = "https://example.com/licenses.json"
    output_file = "output.json"

    with mock.patch("src.update.spdx_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        with mock.patch("builtins.open", mock.mock_open()):
            download_spdx_license_list(url, output_file)
            mock_logger.debug.assert_called_with("Failed to download SPDX license list.")


# Test for load_spdx_license_list
def test_load_spdx_license_list(mock_logger):
    filepath = "test.json"
    json_data = {"licenses": []}

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(json_data))):
        result = load_spdx_license_list(filepath)
        assert result == json_data


# Test for delete_file
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


# Test for create_json
def test_process_json_dump(mock_logger):
    input_file = "licenses.json"
    license_data = {"licenses": [{"licenseId": "TEST", "name": "TEST License"}]}

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(license_data))), \
         mock.patch("src.update.spdx_data_update.build_canonical_dictionary"), \
         mock.patch("src.update.spdx_data_update.check_canonical_name_with_file"), \
         mock.patch("json.dump") as mock_json_dump:
        process_json(input_file, is_exception=False)
        mock_json_dump.assert_called_once()


def test_process_json_already_exists(mock_logger):
    input_file = "spdx_license_list.json"
    spdx_license_data = {"licenses": [{"licenseId": "MIT", "name": "MIT License"}]}

    output_file = os.path.join(DATA_DIR, "MIT.json")
    mit_license_data = {"canonical": "MIT", "src": "spdx"}

    mock_open_instance = mock.mock_open()

    mock_open_instance.side_effect = [
        mock.mock_open(read_data=json.dumps(spdx_license_data)).return_value,
        mock.mock_open(read_data=json.dumps(mit_license_data)).return_value
    ]

    with mock.patch("builtins.open", mock_open_instance), \
         mock.patch("src.update.spdx_data_update.build_canonical_dictionary"), \
         mock.patch("src.update.spdx_data_update.check_canonical_name_with_file"), \
         mock.patch("json.dump") as mock_json_dump:
        process_json(input_file, is_exception=False)
        mock_logger.debug.assert_called_once_with(f"License already exists: {output_file}")
        mock_json_dump.assert_not_called()


def test_process_json_exception_dump(mock_logger):
    input_file = "licenses.json"
    license_data = {"exceptions": [{"licenseExceptionId": "TEST_exception", "name": "TEST_exception License"}]}

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(license_data))), \
         mock.patch("src.update.spdx_data_update.build_canonical_dictionary"), \
         mock.patch("src.update.spdx_data_update.check_canonical_name_with_file"), \
         mock.patch("json.dump") as mock_json_dump:
        process_json(input_file, is_exception=True)
        mock_json_dump.assert_called_once()


def test_process_json_exception_already_exists(mock_logger):
    input_file = "licenses.json"
    spdx_exception_data = \
        {"exceptions": [{"licenseExceptionId": "389-exception", "name": "389 Directory Server Exception"}]}

    output_file = os.path.join(DATA_DIR, "389-exception.json")
    exception_license_data = {"canonical": "389-exception", "src": "spdx"}

    mock_open_instance = mock.mock_open()

    mock_open_instance.side_effect = [
        mock.mock_open(read_data=json.dumps(spdx_exception_data)).return_value,
        mock.mock_open(read_data=json.dumps(exception_license_data)).return_value
    ]

    with mock.patch("builtins.open", mock_open_instance), \
        mock.patch("src.update.spdx_data_update.build_canonical_dictionary"), \
         mock.patch("src.update.spdx_data_update.check_canonical_name_with_file"), \
         mock.patch("json.dump") as mock_json_dump:
        process_json(input_file, is_exception=True)
        mock_logger.debug.assert_called_once_with(f"License already exists: {output_file}")
        mock_json_dump.assert_not_called()


def test_remove_duplicate_licenses(mock_logger):
    duplicate_aliases = {
        "MIT License": ["non_deprecated.json", "deprecated.json"]
    }

    non_deprecated_data = {
        "canonical": "MIT",
        "aliases": {"spdx": []}
    }

    deprecated_data = {
        "canonical": "MIT-deprecated"
    }

    with mock.patch("builtins.open", mock.mock_open()) as mock_file, \
         mock.patch("json.load") as mock_json_load, \
         mock.patch("src.update.spdx_data_update.delete_file") as mock_delete_file:
        # Return non-deprecated data for the first file, and deprecated data for the second file
        mock_json_load.side_effect = [non_deprecated_data, deprecated_data]

        remove_duplicate_licenses(duplicate_aliases)

        # Ensure that the first file is read
        mock_file.assert_any_call("non_deprecated.json", 'r')

        # Ensure that the second file is read
        mock_file.assert_any_call("deprecated.json", 'r')

        # Check that the deprecated file is deleted
        mock_delete_file.assert_called_once_with("deprecated.json")

        # Check if the deprecated canonical name was added to non-deprecated aliases
        assert "MIT-deprecated" in non_deprecated_data["aliases"]["spdx"]


def test_collect_duplicates_non_deprecated():
    duplicate_aliases = {}
    is_deprecated = False
    output_file = "non_deprecated.json"
    name = "MIT License"

    collect_duplicates(duplicate_aliases, is_deprecated, output_file, name)

    # Check that the non-deprecated file is placed at the start of the list
    assert duplicate_aliases[name] == [output_file]


def test_collect_duplicates_deprecated():
    duplicate_aliases = {}
    is_deprecated = True
    output_file = "deprecated.json"
    name = "MIT License"

    collect_duplicates(duplicate_aliases, is_deprecated, output_file, name)

    # Check that the deprecated file is appended
    assert duplicate_aliases[name] == [output_file]


def test_check_canonical_name_with_file(mock_logger):
    canonical_to_file = {
        "MIT": "old_file_path.json"
    }

    license_id = "MIT"
    output_file = "new_file_path.json"

    with mock.patch("os.rename") as mock_rename:
        check_canonical_name_with_file(canonical_to_file, license_id, output_file)

        # Check if os.rename is called to rename the file
        mock_rename.assert_called_once_with("old_file_path.json", output_file)

        # Ensure that the canonical_to_file mapping is updated
        assert canonical_to_file[license_id] == output_file


def test_build_canonical_dictionary(mock_logger):
    canonical_to_file = {}
    files_in_dir = ["MIT.json", "GPL.json"]

    # Mock the data in these files
    mit_data = {"canonical": "MIT"}
    gpl_data = {"canonical": "GPL-3.0"}

    with mock.patch("os.listdir", return_value=files_in_dir), \
         mock.patch("builtins.open", mock.mock_open()) as mock_file, \
         mock.patch("json.load") as mock_json_load:
        # Load the JSON content for each file
        mock_json_load.side_effect = [mit_data, gpl_data]

        build_canonical_dictionary(canonical_to_file)

        # Ensure that the canonical_to_file dictionary is updated correctly
        assert canonical_to_file["MIT"] == os.path.join(DATA_DIR, "MIT.json")
        assert canonical_to_file["GPL-3.0"] == os.path.join(DATA_DIR, "GPL.json")

        # Ensure both files were opened
        mock_file.assert_any_call(os.path.join(DATA_DIR, "MIT.json"), 'r')
        mock_file.assert_any_call(os.path.join(DATA_DIR, "GPL.json"), 'r')


def test_is_spdx_source():
    file_name = "MIT.json"

    # Mock the data in file
    mit_data = {"canonical": "MIT", "src": "scancode-licensedb"}

    with mock.patch("builtins.open", mock.mock_open()), \
         mock.patch("json.load") as mock_json_load:
        mock_json_load.side_effect = [mit_data]

        return_value = is_spdx_source(file_name)

        assert return_value is False


def test_main(mock_logger):
    # Mock the external function calls
    with mock.patch("src.update.spdx_data_update.download_spdx_license_list") as mock_download, \
         mock.patch("src.update.spdx_data_update.process_json") as mock_process_json, \
         mock.patch("src.update.spdx_data_update.delete_file") as mock_delete_file:
        # Call the main function
        from src.update.spdx_data_update import main
        main()

        # Check that download_spdx_license_list was called twice (once for license, once for exception)
        assert mock_download.call_count == 2
        mock_download.assert_any_call(
            "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json",
            "spdx_license_list.json"
        )
        mock_download.assert_any_call(
            "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json",
            "spdx_exceptions.json"
        )

        # Check that create_json was called twice (once for license, once for exception)
        assert mock_process_json.call_count == 2
        mock_process_json.assert_any_call("spdx_license_list.json", is_exception=False)
        mock_process_json.assert_any_call("spdx_exceptions.json", is_exception=True)

        # Check that delete_file was called twice (once for a spdx license file, once for a spdx exception file)
        assert mock_delete_file.call_count == 2
        mock_delete_file.assert_any_call("spdx_license_list.json")
        mock_delete_file.assert_any_call("spdx_exceptions.json")
