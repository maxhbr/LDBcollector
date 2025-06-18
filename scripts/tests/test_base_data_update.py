#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.update.BaseDataUpdate import BaseDataUpdate


@pytest.fixture
def base_data_update():
    return BaseDataUpdate(src="test_source", log_level=10)


@patch("requests.get")
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=True)
def test_download_json_file(mock_exists, mock_open, mock_requests, base_data_update):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"{\"key\": \"value\"}"
    mock_requests.return_value = mock_response

    url = "https://example.com/license.json"
    output_file = "test.json"

    base_data_update.download_json_file(url, output_file)

    mock_requests.assert_called_once_with(url)
    mock_open.assert_called_once_with(output_file, "wb")
    mock_open().write.assert_called_once_with(mock_response.content)


@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
def test_load_json_file(mock_open, base_data_update):
    filepath = "test.json"
    data = base_data_update.load_json_file(filepath)

    mock_open.assert_called_once_with(filepath, "r")
    assert data == {"key": "value"}


@patch("os.remove")
@patch("os.path.exists", return_value=True)
def test_delete_file(mock_exists, mock_remove, base_data_update):
    filepath = "test.json"

    base_data_update.delete_file(filepath)

    mock_exists.assert_called_once_with(filepath)
    mock_remove.assert_called_once_with(filepath)


@patch("os.path.join", return_value="/path/to/license.json")
@patch("builtins.open", new_callable=mock_open,
       read_data='{"canonical": "test", "aliases": {"source": ["alias1"]}, "rejected": ["rejected_alias"], "risky": ["risky_alias"]}')
@patch("json.dump")
def test_update_license_file(mock_json_dump, mock_open, mock_join, base_data_update):
    canonical_id = "test_license"
    aliases = ["alias2"]

    base_data_update.update_license_file(canonical_id, aliases)

    expected_data = {"canonical": "test", "aliases": {"source": ["alias1"], "test_source": ["alias2"]}, "rejected": ["rejected_alias"],
                     "risky": ["risky_alias"]}

    mock_join.assert_called_once()
    mock_open.assert_called_with("/path/to/license.json", "w")
    mock_json_dump.assert_called_once()
    mock_json_dump.assert_called_once_with(expected_data, mock_open(), indent=4)


@patch("os.path.join", return_value="/path/to/license.json")
@patch("builtins.open", new_callable=mock_open,
       read_data='{"canonical": "test", "aliases": {"source": ["alias1"]}, "rejected": ["rejected_alias"], "risky": ["risky_alias"]}')
@patch("json.dump")
def test_update_license_file_rejected_and_risky(mock_json_dump, mock_open, mock_join, base_data_update, caplog):
    canonical_id = "test_license"
    aliases = ["risky_alias", "rejected_alias"]

    base_data_update.update_license_file(canonical_id, aliases)

    expected_data = {"canonical": "test", "aliases": {"source": ["alias1"]}, "rejected": ["rejected_alias"], "risky": ["risky_alias"]}

    mock_join.assert_called_once()
    mock_open.assert_called_with("/path/to/license.json", "w")
    mock_json_dump.assert_called_once()
    assert caplog.text.__contains__("For test_license the alias 'risky_alias' is already in risky list")
    assert caplog.text.__contains__("For test_license the alias 'rejected_alias' is already in rejected list")
    mock_json_dump.assert_called_once_with(expected_data, mock_open(), indent=4)


@patch("os.path.join", return_value="/path/to/data/license.json")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_create_license_file(mock_json_dump, mock_open, mock_join, base_data_update):
    canonical_id = "test_license"
    aliases = ["alias1", "alias2"]

    base_data_update.create_license_file(canonical_id, aliases)

    mock_join.assert_called_once()
    mock_open.assert_called_once_with("/path/to/data/license.json", "w")
    mock_json_dump.assert_called_once()
    expected_data = {
        "canonical": canonical_id,
        "aliases": {
            "test_source": aliases,
            "custom": []
        },
        "src": "test_source",
        "rejected": [],
        "risky": []

    }
    mock_json_dump.assert_called_once_with(expected_data, mock_open(), indent=4)
