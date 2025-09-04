import json
import src.update.update_major_version_only as update_major_version_only


def test_get_non_unique():
    numbers = [1, 2, 2, 3, 4, 4, 4, 5]
    result = update_major_version_only._get_non_unique(numbers)
    # Using sorted because order is not important
    assert sorted(result) == [2, 4]


def test_build_dict_with_base_name_license():
    licenses_list = [
        ("abc1.0", ["1.0"]),
        ("abc2.0", ["2.0"]),
        ("def1.0", ["1.0"])
    ]
    result = update_major_version_only._build_dict_with_base_name_license(licenses_list)
    # For "abc", base name will be "abc" and multiple entries will be kept,
    # while "def" (only one entry) is removed.
    expected = {"abc": [("abc1.0", 1), ("abc2.0", 2)]}
    assert result == expected


def test_identify_major_only_licenses():
    # Prepare a base_name_dict with one base that has duplicate major versions and one that does not.
    base_name_dict = {
        "abc": [("abc1.0", 1), ("abc1.0", 1)],
        "def": [("def1.0", 1), ("def2.0", 2)],
        "ghi": [("ghi1.0", 1), ("ghi1.1.1", 1),("ghi2.0", 2)]
    }
    major_only, not_major_only = update_major_version_only._identify_major_only_licenses(base_name_dict)
    # For base "abc", the version 1 appears twice so both should be classified as non-major-only.
    # For base "def", no duplicates so both licenses go into major-only.
    assert sorted(major_only) == sorted(["def1.0", "def2.0", "ghi2.0"])
    assert sorted(not_major_only) == sorted(["abc1.0", "abc1.0", "ghi1.0", "ghi1.1.1"])


def test_extract_license_list_with_semver(tmp_path, monkeypatch):
    # Create a dummy JSON file with a "canonical" field.
    file_content = {"canonical": "license1.0"}
    json_file = tmp_path / "test_file.json"
    json_file.write_text(json.dumps(file_content))

    # Override DATA_DIR to use the temporary path, set JSON_EXTENSION, and stub out extract_version_tokens.
    monkeypatch.setattr(update_major_version_only, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(update_major_version_only, "JSON_EXTENSION", ".json")
    # For testing purposes, define extract_version_tokens to return ["1.0"] if canonical equals "license1.0"
    monkeypatch.setattr(
        update_major_version_only,
        "extract_version_tokens",
        lambda canonical: ["1.0"] if canonical == "license1.0" else []
    )

    licenses_list = []
    update_major_version_only._extract_license_list_with_semver(licenses_list)
    # Expect that the file is processed and the tuple is added.
    assert licenses_list == [("license1.0", ["1.0"])]


def test_write_to_license_file(tmp_path, monkeypatch):
    monkeypatch.setattr(update_major_version_only, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(update_major_version_only, "JSON_EXTENSION", ".json")

    lic = "testlicense"
    file_path = tmp_path / (lic + ".json")
    original_data = {"dummy": "data"}
    file_path.write_text(json.dumps(original_data))

    # Call the function to update the file flag to True and verify the update.
    update_major_version_only._write_to_license_file([lic], is_major_version_only=True)
    updated_data = json.loads(file_path.read_text())
    assert updated_data.get("isMajorVersionOnly") is True

    # Then update the file flag to False and verify.
    update_major_version_only._write_to_license_file([lic], is_major_version_only=False)
    updated_data = json.loads(file_path.read_text())
    assert updated_data.get("isMajorVersionOnly") is False


def test_update_flag_in_licence_files(tmp_path, monkeypatch):
    monkeypatch.setattr(update_major_version_only, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(update_major_version_only, "JSON_EXTENSION", ".json")

    major_licenses = ["major_license"]
    non_major_licenses = ["non_major_license"]

    # Create dummy JSON files for each license.
    for lic in major_licenses + non_major_licenses:
        file_path = tmp_path / (lic + ".json")
        file_path.write_text(json.dumps({"content": "dummy"}))

    # Call _update_flag_in_licence_files to update the flags.
    update_major_version_only._update_flag_in_licence_files(major_licenses, non_major_licenses)

    # Verify that the major licenses were updated with True and non-major licenses with False.
    for lic in major_licenses:
        file_path = tmp_path / (lic + ".json")
        data = json.loads(file_path.read_text())
        assert data.get("isMajorVersionOnly") is True

    for lic in non_major_licenses:
        file_path = tmp_path / (lic + ".json")
        data = json.loads(file_path.read_text())
        assert data.get("isMajorVersionOnly") is False
