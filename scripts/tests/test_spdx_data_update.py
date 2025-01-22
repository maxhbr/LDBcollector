import os.path

import pytest
from unittest.mock import patch, mock_open
from src.update.SpdxDataUpdate import SpdxDataUpdate


@pytest.fixture
def spdx_data_update():
    return SpdxDataUpdate()


@patch("os.rename")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_update_non_spdx_license_file(mock_json_dump, mock_open, mock_rename, spdx_data_update):
    license_id = "SPDX-License"
    data = {
        "canonical": "old-license",
        "aliases": {
            "custom": ["Some Alias"],
            "other-source": ["SPDX-License", "old-license-alias"]
        },
        "src": "other-source"
    }
    old_license_filepath = "old-path/old-license.json"
    license_name = "SPDX License Name"

    spdx_data_update.update_non_spdx_license_file(license_id, data, old_license_filepath, license_name)

    assert data["canonical"] == license_id
    assert data["src"] == "spdx"
    assert data["aliases"]["other-source"] == ["old-license-alias", "old-license"]
    assert data["aliases"]["spdx"] == [license_name]

    new_filepath = os.path.join(spdx_data_update.DATA_DIR, f"{license_id}.json")
    mock_rename.assert_called_once_with(old_license_filepath, new_filepath)
    mock_json_dump.assert_called_once()


@patch("os.listdir", return_value=["file1.json", "file2.json"])
@patch("builtins.open", new_callable=mock_open, read_data='{"aliases": {"source": ["alias1", "alias2"]}}')
def test_get_file_for_unrecognised_id(mock_open, mock_listdir, spdx_data_update):
    license_name_variations = ["alias2", "unknown-alias"]

    result = spdx_data_update.get_file_for_unrecognised_id(license_name_variations)

    assert result == "file1.json"
    assert mock_listdir.call_count == 2


@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.get_file_for_unrecognised_id", return_value=None)
def test_process_unrecognized_license_id_file_not_found(mock_get_file, spdx_data_update):
    aliases = ["alias1", "alias2"]
    license_id = "unknown-license"

    result = spdx_data_update.process_unrecognized_license_id(aliases, license_id)

    assert result == license_id
    mock_get_file.assert_called_once()


@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.get_file_for_unrecognised_id", return_value="test.json")
@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.update_license_file")
@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.update_non_spdx_license_file")
@patch("builtins.open", new_callable=mock_open, read_data='{"src": "other-source"}')
def test_process_unrecognized_license_id_found_non_spdx(mock_open, mock_update_non_spdx, mock_update_license,
                                                        mock_get_file, spdx_data_update):
    aliases = ["alias1"]
    license_id = "test-license"

    result = spdx_data_update.process_unrecognized_license_id(aliases, license_id)

    assert result is None
    mock_get_file.assert_called_once()
    mock_update_non_spdx.assert_called_once()
    mock_update_license.assert_not_called()


@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.download_json_file")
@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.load_json_file")
@patch("os.listdir", return_value=["id1.json"])
@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.update_license_file")
@patch("src.update.SpdxDataUpdate.SpdxDataUpdate.delete_file")
def test_process_licenses(mock_delete_file, mock_update_license, mock_listdir, mock_load_json, mock_download_json,
                          spdx_data_update):
    # Mock the behavior of load_json_file for different calls
    mock_load_json.side_effect = [
        # First call: return SPDX licenses list
        {"licenses": [{"licenseId": "id1", "name": "name1"}]},
        # Second call: return the content of the id1.json file
        {"src": "spdx"}
    ]

    result = spdx_data_update._process_licenses("dummy_url", "licenseId", "licenses")

    # Assertions
    mock_download_json.assert_called_once_with("dummy_url", "spdx_license_list.json")
    mock_listdir.assert_called_once_with(spdx_data_update.DATA_DIR)
    mock_load_json.assert_any_call("spdx_license_list.json")
    mock_load_json.assert_any_call(os.path.join(spdx_data_update.DATA_DIR, "id1.json"))
    mock_update_license.assert_called_once_with("id1", ["name1"])
    mock_delete_file.assert_called_once_with("spdx_license_list.json")

    assert result == []  # No unprocessed licenses


@patch("src.update.SpdxDataUpdate.SpdxDataUpdate._process_licenses", side_effect=[["license1"], []])
def test_process_licenses_summary(mock_process, spdx_data_update, caplog):
    spdx_data_update.process_licenses()

    assert caplog.text.__contains__("Processed 1.\n{'licenses': ['license1'], 'exceptions': []}")
    mock_process.assert_called()
