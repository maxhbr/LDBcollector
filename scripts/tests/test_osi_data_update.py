import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
from unittest import mock
from src.update.OsiDataUpdate import OsiDataUpdate


def test_get_aliases(capsys):
    entry = {
        "id": "MIT",
        "name": "MIT License",
        "other_names": [{"name": "MIT"}]
    }

    alias = OsiDataUpdate.get_aliases(entry)
    assert set(alias) == {"MIT", "MIT License"}


def test_extract_url_id(capsys):
    entry = {
        "links": [
            {
                "note": "Wikipedia page",
                "url": "https://en.wikipedia.org/wiki/MIT_License"
            },
            {
                "note": "OSI Page",
                "url": "https://opensource.org/licenses/mit"
            }]
    }

    url_id = OsiDataUpdate.extract_url_id(entry)
    assert "mit" == url_id


def test_process_unrecognized_license_id_recognized(capsys):
    aliases = ["The MIT License", "MIT License"]
    canonical_id = "mit"
    data = {
        "canonical": canonical_id,
        "aliases": {
            "osi": [],
            "spdx": ["MIT License"]
        }
    }
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))), mock.patch("json.dump"):
        osi_data_update = OsiDataUpdate()
        result = osi_data_update.process_unrecognized_license_id(aliases, canonical_id, "")

        assert result is None


def test_process_unrecognized_license_id_recognized_still_unrecognized(capsys):
    aliases = ["The MIT License", "MIT License"]
    canonical_id = "mit"
    data = {
        "canonical": "MIT",
        "aliases": {
            "osi": [],
            "spdx": []
        }
    }
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))), mock.patch("json.dump"):
        osi_data_update = OsiDataUpdate()
        result = osi_data_update.process_unrecognized_license_id(aliases, canonical_id, "")

        assert result == "mit"


@pytest.fixture
def osi_data_update():
    """Fixture to initialize the OsiDataUpdate instance."""
    updater = OsiDataUpdate()
    updater._LOGGER = MagicMock()  # Mock the logger
    updater._DATA_DIR = "mock_data_dir"  # Mock data directory
    return updater


def test_process_licenses(osi_data_update):
    # Mock data
    mock_license_list = [
        {
            "id": "license-1",
            "links": [{"note": "OSI Page", "url": "https://opensource.org/licenses/license-1"}],
            "name": "Test License 1",
            "other_names": [{"name": "License One"}]
        },
        {
            "id": "license-2",
            "links": [{"note": "OSI Page", "url": "https://opensource.org/licenses/license-2"}],
            "name": "Test License 2",
            "other_names": []
        },
    ]
    mock_files_list = ["license-1.json"]  # Existing file in the directory

    # Mock the dependencies
    osi_data_update.download_json_file = MagicMock()
    osi_data_update.load_json_file = MagicMock(return_value=mock_license_list)
    osi_data_update.update_license_file = MagicMock()
    osi_data_update.delete_file = MagicMock()

    # Mock os.listdir to return mock files
    with patch("os.listdir", return_value=mock_files_list):
        # Mock open for reading JSON files
        mock_file_data = json.dumps({"aliases": {"osi": ["Test License 1", "License One"]}})
        with patch("builtins.open", mock_open(read_data=mock_file_data)):
            # Call the method under test
            osi_data_update.process_licenses()

            # Assertions
            osi_data_update.download_json_file.assert_called_once_with(
                "https://api.opensource.org/licenses/", "osi_license_list.json"
            )
            osi_data_update.load_json_file.assert_called_once_with("osi_license_list.json")

            # Check if update_license_file was called for license-1
            osi_data_update.update_license_file.assert_any_call(
                "license-1",
                ["Test License 1", "License One", "license-1"],
            )

            # Check if update_license_file was not called for license-2
            osi_data_update.update_license_file.assert_called_once()

            osi_data_update.delete_file.assert_called_once_with("osi_license_list.json")
            osi_data_update._LOGGER.info.assert_any_call("Unprocessed licenses: 1\n['license-2']")
