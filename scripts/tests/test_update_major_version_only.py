import json
import src.update.update_major_version_only as update_major_version_only


def test_get_non_unique():
    numbers = [1, 2, 2, 3, 4, 4, 4, 5]
    result = update_major_version_only._get_non_unique(numbers)

    assert sorted(result) == [2, 4]


def test_build_dict_with_base_name_license():
    licenses_list = [
        ("abc1.0", ["1.0"]),
        ("abc2.0", ["2.0"]),
        ("def1.0", ["1.0"]),
        ("ghi1.0", ["2.0", "3.0"])
    ]
    result = update_major_version_only.build_dict_with_base_name_license(licenses_list)

    expected = {"abc": [("abc1.0", 1), ("abc2.0", 2)], "def": [("def1.0", 1)]}
    assert result == expected


def test_identify_major_only_licenses():
    base_name_dict = {
        "abc": [("abc1.0", 1), ("abc1.0", 1)],
        "def": [("def1.0", 1), ("def2.0", 2)],
        "ghi": [("ghi1.0", 1), ("ghi1.1.1", 1), ("ghi2.0", 2)]
    }
    major_only, not_major_only = update_major_version_only._identify_major_only_licenses(base_name_dict)

    assert sorted(major_only) == sorted(["def1.0", "def2.0", "ghi2.0"])
    assert sorted(not_major_only) == sorted(["abc1.0", "abc1.0", "ghi1.0", "ghi1.1.1"])


def test_write_to_license_file(tmp_path, monkeypatch):
    monkeypatch.setattr(update_major_version_only, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(update_major_version_only, "JSON_EXTENSION", ".json")

    lic = "testlicense"
    file_path = tmp_path / (lic + ".json")
    original_data = {"dummy": "data"}
    file_path.write_text(json.dumps(original_data))

    update_major_version_only._write_to_license_file([lic], is_major_version_only=True)
    updated_data = json.loads(file_path.read_text())
    assert updated_data.get("isMajorVersionOnly") is True

    update_major_version_only._write_to_license_file([lic], is_major_version_only=False)
    updated_data = json.loads(file_path.read_text())
    assert updated_data.get("isMajorVersionOnly") is False


def test_update_flag_in_licence_files(tmp_path, monkeypatch):
    monkeypatch.setattr(update_major_version_only, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(update_major_version_only, "JSON_EXTENSION", ".json")

    major_licenses = ["major_license"]
    non_major_licenses = ["non_major_license"]

    for lic in major_licenses + non_major_licenses:
        file_path = tmp_path / (lic + ".json")
        file_path.write_text(json.dumps({"content": "dummy"}))

    update_major_version_only._update_flag_in_licence_files(major_licenses, non_major_licenses)

    for lic in major_licenses:
        file_path = tmp_path / (lic + ".json")
        data = json.loads(file_path.read_text())
        assert data.get("isMajorVersionOnly") is True

    for lic in non_major_licenses:
        file_path = tmp_path / (lic + ".json")
        data = json.loads(file_path.read_text())
        assert data.get("isMajorVersionOnly") is False
