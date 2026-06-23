#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import os
import json
import pytest
from unittest import mock

from src.validate import data_validation
from src.validate.data_validation import (
    download_license_list,
    load_ids_from_license_list,
    delete_file,
    check_json_filename,
    check_unique_aliases,
    check_length_and_characters,
    check_src_and_canonical,
    LicenseListType,
    check_no_empty_field_except_custom,
    check_rejected_field_exists,
    check_rejected_not_in_valid_fields,
    check_version_between_canonical_and_alias,
    check_canonical_source_is_valid,
    check_valid_alias_keys,
    validate_license_data,
    validate_orgs_licenses,
    validate_unique_orgs,
    validate_equal_source_and_org_names,
    validate_org_names_not_forbidden,
    check_no_overlap_between_oss_and_orgs,
    collect_identifiers_from_dir
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
    test_data = {"canonical": {"id": "correct_name"}}
    filepath = os.path.join("test_data", "correct_name.json")
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_json_filename("test_data")

    mock_logger.error.assert_not_called()


def test_check_json_filename_failure():
    canonical_name = "correct_name"
    test_data = {"canonical": {"id": canonical_name}}

    filename = "incorrect_name.json"
    filepath = os.path.join("test_data", filename)
    os.makedirs("test_data", exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_json_filename("test_data")

    mock_logger.error.assert_called_with(f"JSON filename '{filename}' does not match canonical id '{canonical_name}'")


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

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_unique_aliases("test_data")

    mock_logger.error.assert_not_called()


def test_check_unique_aliases_failure():
    alias_duplicate = "alias1"
    test_data1 = {"aliases": {"SPDX": [alias_duplicate, "alias2"]}}
    test_data2 = {"aliases": {"SPDX": [alias_duplicate, "alias4"]}}

    filenames = ["file1.json", "file2.json"]
    filepath1 = os.path.join("test_data", filenames[0])
    filepath2 = os.path.join("test_data", filenames[1])

    dump_files(filepath1, filepath2, test_data1, test_data2)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_unique_aliases("test_data")

    mock_logger.mock_calls.__contains__(f"Alias '{alias_duplicate}' is not unique globally.")


def test_check_src_and_canonical():
    spdx_licenses = ["MIT", "Apache-2.0"]
    test_data = {"canonical": {"id": "MIT", "src": "spdx"}}

    os.makedirs("test_data", exist_ok=True)
    filepath = os.path.join("test_data", "test_file.json")

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_src_and_canonical(spdx_licenses, [], "test_data")

    mock_logger.error.assert_not_called()


def test_check_src_and_canonical_failure_source_not_spdx():
    spdx_licenses = ["MIT", "Apache-2.0"]
    test_data = {"canonical": {"id": "MIT", "src": "Not-SPDX"}}

    filepath = os.path.join("test_data", "test_file.json")

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_src_and_canonical(spdx_licenses, [], "test_data")

    mock_logger.error.assert_called_with(
        "If src is SPDX, canonical name 'MIT' must be in SPDX license list")


def test_check_src_and_canonical_failure_source_is_spdx():
    spdx_licenses = ["MIT", "Apache-2.0"]
    canonical_name = "NO_SPDX_LICENSE"
    test_data = {"canonical": {"id": canonical_name, "src": "spdx"}}

    filepath = os.path.join("test_data", "test_file.json")

    with open(filepath, 'w') as f:
        json.dump(test_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_src_and_canonical(spdx_licenses, [], "test_data")

    mock_logger.error.assert_called_with(
        f"Canonical name '{canonical_name}' is in SPDX license list but source is not 'spdx'.")


def test_check_length_and_characters():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"canonical": {"id": "valid_name", "src": "valid_src"}, "aliases": {"spdx": ["valid_alias", "valid_alias2"]}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_length_and_characters("test_data")

    assert mock_logger.error.call_count == 0


def test_check_length_and_characters_failure():
    max_length = 100

    os.makedirs("test_data", exist_ok=True)

    src_too_long = "a" * (max_length + 1)
    long_data = {"canonical": {"id": "a" * (max_length + 1), "src": src_too_long},
                 "aliases": {"spdx": ["a" * (max_length + 1)], "custom": []}}
    forbidden_data = {"canonical": {"id": "invalid#name", "src": "src"}, "aliases": {"spdx": ["alias1"], "custom": []}}

    filepath_long = os.path.join("test_data", "long.json")
    filepath_forbidden = os.path.join("test_data", "forbidden.json")

    with open(filepath_long, 'w') as f:
        json.dump(long_data, f)

    with open(filepath_forbidden, 'w') as f:
        json.dump(forbidden_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_length_and_characters("test_data")

    # Check for long strings
    mock_logger.error.assert_any_call(f"Canonical id '{long_data['canonical']['id']}' exceeds maximum length "
                                      f"limit of {max_length} characters")

    mock_logger.error.assert_any_call(f"At least one of the aliases exceeds maximum length limit of "
                                      f"{max_length} characters in the file long.json")

    mock_logger.error.assert_any_call(
        f"Source {src_too_long} exceeds maximum length limit of {max_length} characters")

    # Check for forbidden characters
    mock_logger.error.assert_any_call(
        f"Canonical id '{forbidden_data['canonical']['id']}' contains forbidden characters")


def test_check_no_empty_field_except_custom_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"custom": [], "canonical": {"id": "valid_name", "src": "valid_src"},
                  "aliases": {"spdx": ["valid_alias", "valid_alias2"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_empty_field_except_custom("test_data")

    assert mock_logger.error.call_count == 0


def test_check_no_empty_field_except_custom_failure():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"custom": [], "canonical": {"id": "", "src": "valid_src"},
                  "aliases": {"spdx": ["valid_alias", "valid_alias2"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_empty_field_except_custom("test_data")

    assert mock_logger.error.call_count == 1


def test_check_rejected_field_exists_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": [], "canonical": "valid_name", "src": "valid_src", "aliases": ["valid_alias", "valid_alias2"]}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_rejected_field_exists("test_data")

    assert mock_logger.error.call_count == 0


def test_check_rejected_field_exists_failure():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"canonical": "valid_name", "src": "valid_src", "aliases": {"spdx": ["valid_alias", "valid_alias2"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_rejected_field_exists("test_data")

    assert mock_logger.error.call_count == 1


def test_check_rejected_not_in_valid_fields_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": "valid_name", "src": "valid_src",
                  "aliases": {"spdx": ["valid_alias", "valid_alias2"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_rejected_not_in_valid_fields("test_data")

    assert mock_logger.error.call_count == 0


def test_check_rejected_not_in_valid_fields_failure():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": "valid_name", "src": "valid_src",
                  "aliases": {"spdx": ["not_valid_alias", "valid_alias2"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_rejected_not_in_valid_fields("test_data")

    assert mock_logger.error.call_count == 1


def test_check_version_between_canonical_and_alias_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                  "aliases": {"spdx": ["The Valid License"], "scancode-licensedb": ["valid_alias_1.0"], "custom": ["vl 1.0"]}}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")

    assert mock_logger.error.call_count == 0


def test_check_version_between_canonical_and_alias_failure(caplog):
    os.makedirs("test_data", exist_ok=True)

    invalid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                    "aliases": {"scancode-licensedb": ["invalid_alias_version"], "custom": ["wrong_version_3.0_1.0"]}}

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_2.0", "src": "valid_src"},
                  "aliases": {"scancode-licensedb": ["valid_alias_version_2.0"], "custom": ["wrong_version_2.0"]}}

    filepath_valid = os.path.join("test_data", "valid.json")
    filepath_valid2 = os.path.join("test_data", "valid2.json")
    with open(filepath_valid, 'w') as f:
        json.dump(invalid_data, f)
    with open(filepath_valid2, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")

    assert mock_logger.error.call_count == 1
    assert str(mock_logger.method_calls).__contains__(
        "valid.json has wrong versions for aliases: ['invalid_alias_version', 'wrong_version_3.0_1.0']")


def test_check_version_between_canonical_and_alias_major_version_only_flag_is_false(caplog):
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                  "aliases": {"custom": ["wrong_version_1"]}, "isMajorVersionOnly": False}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")

    assert mock_logger.error.call_count == 1
    assert str(mock_logger.method_calls).__contains__("valid.json has wrong versions for aliases: ['wrong_version_1']")


def test_check_version_between_canonical_and_alias_major_version_only_flag_is_true(caplog):
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                  "aliases": {"custom": ["wrong_version_1"]}, "isMajorVersionOnly": True}

    filepath_valid = os.path.join("test_data", "valid.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")

    assert mock_logger.error.call_count == 0


def test_check_major_version_flag(caplog):
    test_dir = "test_data"
    os.makedirs(test_dir, exist_ok=True)

    # Group 1: "Apache-" group
    # Expected: major version 1 appears twice so expected flag should be False,
    # while major version 2 appears once so expected flag should be True.
    apache_1_0 = {"canonical": {"id": "Apache-1.0"}, "isMajorVersionOnly": False}
    apache_1_1 = {"canonical": {"id": "Apache-1.1"}, "isMajorVersionOnly": True}
    apache_2_0 = {"canonical": {"id": "Apache-2.0"}, "isMajorVersionOnly": True}

    with open(os.path.join(test_dir, "Apache-1.0.json"), "w") as f:
        json.dump(apache_1_0, f)
    with open(os.path.join(test_dir, "Apache-1.1.json"), "w") as f:
        json.dump(apache_1_1, f)
    with open(os.path.join(test_dir, "Apache-2.0.json"), "w") as f:
        json.dump(apache_2_0, f)

    # Group 2: "GPL-" group (both files expected to have True as they have unique major versions)
    gpl_2_0 = {"canonical": {"id": "GPL-2.0"}, "isMajorVersionOnly": True}
    gpl_3_0 = {"canonical": {"id": "GPL-3.0"}, "isMajorVersionOnly": True}
    with open(os.path.join(test_dir, "GPL-2.0.json"), "w") as f:
        json.dump(gpl_2_0, f)
    with open(os.path.join(test_dir, "GPL-3.0.json"), "w") as f:
        json.dump(gpl_3_0, f)

    # Group 3: File with canonical without a version token (will be skipped)
    noversion = {"canonical": {"id": "LicenseNoVersion"}}
    with open(os.path.join(test_dir, "LicenseNoVersion.json"), "w") as f:
        json.dump(noversion, f)

    # Group 4: A file that alone makes its own group (skipped because group size is 1)
    unique = {"canonical": {"id": "UniqueLicense-1.0"}, "isMajorVersionOnly": True}
    with open(os.path.join(test_dir, "UniqueLicense-1.0.json"), "w") as f:
        json.dump(unique, f)

    # Group 5: A license file which should have isMajorVersionOnly flag set to true but isn't
    mit_4_0 = {"canonical": {"id": "MIT-4.0"}, "isMajorVersionOnly": False}  # Incorrect: Expected True.

    with open(os.path.join(test_dir, "MIT-4.0.json"), "w") as f:
        json.dump(mit_4_0, f)

    caplog.clear()

    data_validation.check_major_version_flag(test_dir)

    error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]

    assert any("Apache-1.1.json" in msg and "expected False" in msg for msg in error_messages)
    assert any("MIT-4.0.json" in msg and "expected True" in msg for msg in error_messages)

    for filename in ["GPL-2.0.json", "GPL-3.0.json", "UniqueLicense-1.0.json", "LicenseNoVersion.json"]:
        assert not any(filename in msg for msg in error_messages)


def test_extract_license_list_with_semver(tmp_path, monkeypatch):
    file_content = {"canonical": {"id": "license1.0"}}
    json_file = tmp_path / "test_file.json"
    json_file.write_text(json.dumps(file_content))

    monkeypatch.setattr(
        data_validation,
        "extract_version_tokens",
        lambda canonical: ["1.0"] if canonical == "license1.0" else []
    )

    licenses_list = []
    data_validation.extract_license_list_with_semver(licenses_list, str(tmp_path))

    assert licenses_list == [("license1.0", ["1.0"])]


def test_only_base_name_with_version_success(caplog):
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                  "aliases": {"scancode-licensedb": ["invalid_alias_version"], "custom": ["major_version_only_v1"]},
                  "isMajorVersionOnly": True}

    other_base_name_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "different_base_name_1.0", "src": "valid_src"},
                            "aliases": {"scancode-licensedb": ["valid_alias_version_1.0"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")
    filepath_valid2 = os.path.join("test_data", "valid2.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)
    with open(filepath_valid2, 'w') as f:
        json.dump(other_base_name_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")
    assert mock_logger.error.call_count == 0


def test_only_base_name_with_version_failure(caplog):
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "valid_name_1.0", "src": "valid_src"},
                  "aliases": {"scancode-licensedb": ["invalid_alias_version"], "custom": ["major_version_only_v1"]}}

    other_base_name_data = {"rejected": ["not_valid_alias"], "canonical": {"id": "different_base_name_1.0", "src": "valid_src"},
                            "aliases": {"scancode-licensedb": ["valid_alias_version_1.0"], "custom": []}}

    filepath_valid = os.path.join("test_data", "valid.json")
    filepath_valid2 = os.path.join("test_data", "valid2.json")

    with open(filepath_valid, 'w') as f:
        json.dump(valid_data, f)
    with open(filepath_valid2, 'w') as f:
        json.dump(other_base_name_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_version_between_canonical_and_alias("test_data")
    assert mock_logger.error.call_count == 1


def test_check_canonical_source_is_valid_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"canonical": {"id": "MIT", "src": "spdx"}, "aliases": {"spdx": ["MIT License"]}}

    filepath = os.path.join("test_data", "MIT.json")

    with open(filepath, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_canonical_source_is_valid("test_data")

    assert mock_logger.error.call_count == 0


def test_check_canonical_source_is_valid_failure():
    os.makedirs("test_data", exist_ok=True)

    invalid_data = {"canonical": {"id": "MIT", "src": "scancodeLicensedb"}, "aliases": {"spdx": ["MIT License"]}}

    filepath = os.path.join("test_data", "MIT.json")

    with open(filepath, 'w') as f:
        json.dump(invalid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_canonical_source_is_valid("test_data")

    assert mock_logger.error.call_count == 1


def test_check_valid_alias_keys_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {"canonical": {"id": "MIT", "src": "spdx"},
                  "aliases": {"spdx": ["MIT License"], "custom": ["mit"], "scancodeLicensedb": ["mit-license"]}}

    filepath = os.path.join("test_data", "MIT.json")

    with open(filepath, 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_valid_alias_keys("test_data")

    assert mock_logger.error.call_count == 0


def test_check_valid_alias_keys_failure():
    os.makedirs("test_data", exist_ok=True)

    invalid_data = {"canonical": {"id": "MIT", "src": "spdx"},
                    "aliases": {"spdx": ["MIT License"], "custom": ["mit"], "invalid_key": ["bad"]}}

    filepath = os.path.join("test_data", "MIT.json")

    with open(filepath, 'w') as f:
        json.dump(invalid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_valid_alias_keys("test_data")

    assert mock_logger.error.call_count == 1


def test_validate_license_data_success():
    os.makedirs("test_data", exist_ok=True)

    valid_data = {
        "canonical": {"id": "TestLic-1.0", "src": "acme"},
        "aliases": {"custom": ["Test License v1.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }

    with open(os.path.join("test_data", "TestLic-1.0.json"), 'w') as f:
        json.dump(valid_data, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_license_data("test_data")

    assert mock_logger.error.call_count == 0


def test_validate_orgs_licenses_success():
    os.makedirs(os.path.join("test_data", "acme"), exist_ok=True)

    license_a = {
        "canonical": {"id": "OrgLic-1.0", "src": "acme"},
        "aliases": {"custom": ["Org License v1.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }
    license_b = {
        "canonical": {"id": "OrgLic-2.0", "src": "acme"},
        "aliases": {"custom": ["Org License v2.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }

    with open(os.path.join("test_data", "acme", "OrgLic-1.0.json"), 'w') as f:
        json.dump(license_a, f)
    with open(os.path.join("test_data", "acme", "OrgLic-2.0.json"), 'w') as f:
        json.dump(license_b, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_orgs_licenses("test_data")

    assert mock_logger.error.call_count == 0


def test_validate_orgs_licenses_multiple_orgs_success():
    os.makedirs(os.path.join("test_data", "org1"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "org2"), exist_ok=True)

    org1_license = {
        "canonical": {"id": "Foo-1.0", "src": "org1"},
        "aliases": {"custom": ["Foo v1.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }
    org2_license = {
        "canonical": {"id": "Bar-1.0", "src": "org2"},
        "aliases": {"custom": ["Bar v1.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }

    with open(os.path.join("test_data", "org1", "Foo-1.0.json"), 'w') as f:
        json.dump(org1_license, f)
    with open(os.path.join("test_data", "org2", "Bar-1.0.json"), 'w') as f:
        json.dump(org2_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_orgs_licenses("test_data")

    assert mock_logger.error.call_count == 0


def test_validate_orgs_licenses_detects_errors_in_org():
    os.makedirs(os.path.join("test_data", "org1"), exist_ok=True)

    # Filename is "Wrong-1.0.json" but canonical id is "Mismatch-1.0" => triggers check_json_filename error
    bad_license = {
        "canonical": {"id": "Mismatch-1.0", "src": "acme"},
        "aliases": {"custom": ["Mismatch License v1.0"]},
        "isMajorVersionOnly": True,
        "rejected": [],
        "risky": []
    }

    with open(os.path.join("test_data", "org1", "Wrong-1.0.json"), 'w') as f:
        json.dump(bad_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_orgs_licenses("test_data")

    assert mock_logger.error.call_count >= 1


def test_validate_unique_orgs_success():
    os.makedirs(os.path.join("test_data", "org1"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "org2"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "org3"), exist_ok=True)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_unique_orgs("test_data")

    assert mock_logger.error.call_count == 0


def test_validate_unique_orgs_failure():
    os.makedirs(os.path.join("test_data", "org1"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "org2"), exist_ok=True)

    # Simulate duplicate orgs by patching os.listdir to return duplicates
    with mock.patch('src.validate.data_validation.os.listdir', return_value=["org1", "org2", "org1"]):
        with mock.patch('src.validate.data_validation.logger', mock_logger):
            validate_unique_orgs("test_data")

    mock_logger.error.assert_called_once_with("Organization 'org1' is already present in the orgs list.")


def test_validate_equal_source_and_org_names_success():
    os.makedirs(os.path.join("test_data", "testOrg"), exist_ok=True)

    license_a = {"canonical": {"id": "testOrgId", "src": "testOrg"}, "aliases": {"custom": ["testOrg License"]}}
    license_b = {"canonical": {"id": "testOrgIdAlt", "src": "testOrg"}, "aliases": {"custom": ["testOrg License Alt"]}}

    with open(os.path.join("test_data", "testOrg", "testOrgId.json"), 'w') as f:
        json.dump(license_a, f)
    with open(os.path.join("test_data", "testOrg", "testOrgIdAlt.json"), 'w') as f:
        json.dump(license_b, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_equal_source_and_org_names("testOrg", "test_data/testOrg")

    assert mock_logger.error.call_count == 0


def test_validate_equal_source_and_org_names_failure():
    os.makedirs(os.path.join("test_data", "testOrg"), exist_ok=True)

    license_a = {"canonical": {"id": "testOrgId", "src": "wrong_org"}, "aliases": {"custom": ["testOrg License"]}}

    with open(os.path.join("test_data", "testOrg", "testOrgId.json"), 'w') as f:
        json.dump(license_a, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_equal_source_and_org_names("testOrg", "test_data/testOrg")

    assert mock_logger.error.call_count == 1
    mock_logger.error.assert_called_with(
        "File 'testOrgId.json' in organization 'testOrg' has canonical source 'wrong_org' that does not match the organization name."
    )


def test_validate_org_names_not_forbidden_success():
    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_org_names_not_forbidden("testOrg")

    assert mock_logger.error.call_count == 0


def test_validate_org_names_not_forbidden_failure():
    with mock.patch('src.validate.data_validation.logger', mock_logger):
        validate_org_names_not_forbidden("stableMap")
        validate_org_names_not_forbidden("riskyMap")

    assert mock_logger.error.call_count == 2


def test_collect_identifiers_from_dir():
    os.makedirs("test_data", exist_ok=True)

    data = {
        "canonical": {"id": "MIT", "src": "spdx"},
        "aliases": {"spdx": ["MIT License"], "custom": ["mit"]}
    }

    with open(os.path.join("test_data", "MIT.json"), 'w') as f:
        json.dump(data, f)

    result = collect_identifiers_from_dir("test_data")

    assert result == {"MIT", "MIT License", "mit"}


def test_check_no_overlap_between_oss_and_orgs_success():
    os.makedirs(os.path.join("test_data", "oss"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org1"), exist_ok=True)

    oss_license = {
        "canonical": {"id": "MIT", "src": "spdx"},
        "aliases": {"spdx": ["MIT License"], "custom": ["mit"]}
    }
    org_license = {
        "canonical": {"id": "OrgLic-1.0", "src": "org1"},
        "aliases": {"custom": ["Org License v1.0"]}
    }

    with open(os.path.join("test_data", "oss", "MIT.json"), 'w') as f:
        json.dump(oss_license, f)
    with open(os.path.join("test_data", "orgs", "org1", "OrgLic-1.0.json"), 'w') as f:
        json.dump(org_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_overlap_between_oss_and_orgs("test_data/oss", "test_data/orgs")

    assert mock_logger.error.call_count == 0


def test_check_no_overlap_between_oss_and_orgs_detects_org_canonical_in_oss():
    os.makedirs(os.path.join("test_data", "oss"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org1"), exist_ok=True)

    oss_license = {
        "canonical": {"id": "SharedId", "src": "custom"},
        "aliases": {"custom": ["oss-alias"]}
    }
    org_license = {
        "canonical": {"id": "OrgLic", "src": "org1"},
        "aliases": {"custom": ["SharedId"]}
    }

    with open(os.path.join("test_data", "oss", "SharedId.json"), 'w') as f:
        json.dump(oss_license, f)
    with open(os.path.join("test_data", "orgs", "org1", "OrgLic.json"), 'w') as f:
        json.dump(org_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_overlap_between_oss_and_orgs("test_data/oss", "test_data/orgs")

    assert mock_logger.error.call_count == 1
    mock_logger.error.assert_called_with(
        "Identifier 'SharedId' is present in both OSS and organization license data."
    )


def test_check_no_overlap_between_oss_and_orgs_detects_org_alias_in_oss_and_oss_alias_in_org():
    os.makedirs(os.path.join("test_data", "oss"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org1"), exist_ok=True)

    oss_license = {
        "canonical": {"id": "MIT", "src": "spdx"},
        "aliases": {"custom": ["shared-org-alias"]}
    }
    org_license = {
        "canonical": {"id": "OrgLic", "src": "org1"},
        "aliases": {"custom": ["MIT", "shared-org-alias"]}
    }

    with open(os.path.join("test_data", "oss", "MIT.json"), 'w') as f:
        json.dump(oss_license, f)
    with open(os.path.join("test_data", "orgs", "org1", "OrgLic.json"), 'w') as f:
        json.dump(org_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_overlap_between_oss_and_orgs("test_data/oss", "test_data/orgs")

    assert mock_logger.error.call_count == 2
    mock_logger.error.assert_any_call(
        "Identifier 'MIT' is present in both OSS and organization license data."
    )
    mock_logger.error.assert_any_call(
        "Identifier 'shared-org-alias' is present in both OSS and organization license data."
    )


def test_check_no_overlap_between_oss_and_orgs_allows_same_across_orgs():
    os.makedirs(os.path.join("test_data", "oss"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org1"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org2"), exist_ok=True)

    oss_license = {
        "canonical": {"id": "MIT", "src": "spdx"},
        "aliases": {"custom": ["mit"]}
    }
    org1_license = {
        "canonical": {"id": "SharedOrgId", "src": "org1"},
        "aliases": {"custom": ["shared-alias"]}
    }
    org2_license = {
        "canonical": {"id": "SharedOrgId", "src": "org2"},
        "aliases": {"custom": ["shared-alias"]}
    }

    with open(os.path.join("test_data", "oss", "MIT.json"), 'w') as f:
        json.dump(oss_license, f)
    with open(os.path.join("test_data", "orgs", "org1", "SharedOrgId.json"), 'w') as f:
        json.dump(org1_license, f)
    with open(os.path.join("test_data", "orgs", "org2", "SharedOrgId.json"), 'w') as f:
        json.dump(org2_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_overlap_between_oss_and_orgs("test_data/oss", "test_data/orgs")

    assert mock_logger.error.call_count == 0


def test_check_no_overlap_between_oss_and_orgs_multiple_orgs_with_overlap():
    os.makedirs(os.path.join("test_data", "oss"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org1"), exist_ok=True)
    os.makedirs(os.path.join("test_data", "orgs", "org2"), exist_ok=True)

    oss_license = {
        "canonical": {"id": "MIT", "src": "spdx"},
        "aliases": {"custom": ["overlap-from-org2"]}
    }
    org1_license = {
        "canonical": {"id": "MIT", "src": "org1"},
        "aliases": {"custom": ["org1-alias"]}
    }
    org2_license = {
        "canonical": {"id": "OrgLic", "src": "org2"},
        "aliases": {"custom": ["overlap-from-org2"]}
    }

    with open(os.path.join("test_data", "oss", "MIT.json"), 'w') as f:
        json.dump(oss_license, f)
    with open(os.path.join("test_data", "orgs", "org1", "MIT.json"), 'w') as f:
        json.dump(org1_license, f)
    with open(os.path.join("test_data", "orgs", "org2", "OrgLic.json"), 'w') as f:
        json.dump(org2_license, f)

    with mock.patch('src.validate.data_validation.logger', mock_logger):
        check_no_overlap_between_oss_and_orgs("test_data/oss", "test_data/orgs")

    assert mock_logger.error.call_count == 2
    mock_logger.error.assert_any_call(
        "Identifier 'MIT' is present in both OSS and organization license data."
    )
    mock_logger.error.assert_any_call(
        "Identifier 'overlap-from-org2' is present in both OSS and organization license data."
    )


if __name__ == "__main__":
    pytest.main()
