import pytest
import os
import json
from unittest import mock
from src.update.osi_data_update import (
    download_license_list_json, load_json_file, delete_file,
    get_aliases, update_data, process_licenses, extract_url_id, process_unrecognized_license_id
)


# Mock logger to avoid side effects in tests
@pytest.fixture
def mock_logger():
    with mock.patch("src.update.osi_data_update.logger") as logger_mock:
        yield logger_mock


@pytest.fixture
def mock_load_json_file():
    with mock.patch('src.update.osi_data_update.load_json_file') as mock_load_json_file:
        yield mock_load_json_file


@pytest.fixture
def mock_download_license_json():
    with (mock.patch('src.update.osi_data_update.download_license_json')
          as mock_download_license_json_file):
        yield mock_download_license_json_file


@pytest.fixture
def mock_get_aliases():
    with mock.patch('src.update.osi_data_update.get_aliases') as mock_get_alias:
        yield mock_get_alias


@pytest.fixture
def mock_update_data():
    with mock.patch('src.update.osi_data_update.update_data') as mock_update_data:
        yield mock_update_data


def test_download_index_json_success(mock_logger):
    url = "https://example.com/index.json"
    output_file = "output.json"

    with mock.patch("src.update.osi_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"{}"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            download_license_list_json(url, output_file)
            mock_get.assert_called_once_with(url)
            mock_file.assert_called_once_with(output_file, 'wb')
            # noinspection PyArgumentList
            mock_file().write.assert_called_once_with(b"{}")
            mock_logger.debug.assert_called_with("OSI license list downloaded successfully.")


def test_download_index_json_failure(mock_logger):
    url = "https://example.com/index.json"
    output_file = "output.json"

    with mock.patch("src.update.osi_data_update.requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        with mock.patch("builtins.open", mock.mock_open()):
            download_license_list_json(url, output_file)
            mock_logger.debug.assert_called_with("Failed to download OSI license list.")


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


def test_update_data(mock_logger):
    canonical_id = "MIT"
    osi_aliases = ["mit-alt", "MIT License"]

    data = {
        "canonical": canonical_id,
        "aliases": {
            "osi": [],
            "spdx": []
        }
    }

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))) as mock_file, \
         mock.patch("json.dump") as mock_json_dump:
        update_data(canonical_id, osi_aliases)

        expected_file_path = os.path.abspath(os.path.join("../../../data", f"{canonical_id}.json"))

        mock_file.assert_any_call(expected_file_path, 'r')

        mock_file.assert_any_call(expected_file_path, 'w')

        mock_json_dump.assert_called_once()


def test_get_aliases(mock_logger):
    entry = {
        "id": "MIT",
        "name": "MIT License",
        "other_names": [{"name": "MIT",}]
    }

    alias = get_aliases(entry)
    assert set(alias) == {"MIT", "MIT License"}


def test_extract_url_id(mock_logger):
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

    url_id = extract_url_id(entry)
    assert "mit" == url_id


def test_process_unrecognized_license_id_recognized(mock_logger):
    aliases = ["The MIT License", "MIT License"]
    canonical_id = "mit"
    data = {
        "canonical": canonical_id,
        "aliases": {
            "osi": [],
            "spdx": ["MIT License"]
        }
    }
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))), \
         mock.patch("json.dump"):
        result = process_unrecognized_license_id(aliases, canonical_id, "")

        assert result is None


def test_process_unrecognized_license_id_recognized_still_unrecognized(mock_logger):
    aliases = ["The MIT License", "MIT License"]
    canonical_id = "mit"
    data = {
        "canonical": "MIT",
        "aliases": {
            "osi": [],
            "spdx": []
        }
    }
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(data))), \
         mock.patch("json.dump"):
        result = process_unrecognized_license_id(aliases, canonical_id, "")

        assert result == "mit"


# Test for process_licenses function (integration test)
def test_process_licenses(mock_logger):
    with mock.patch("src.update.osi_data_update.download_license_list_json"), \
         mock.patch("src.update.osi_data_update.load_json_file",
                    return_value=[{"id": "mit", "name": "MIT License"}]), \
         mock.patch("src.update.osi_data_update.extract_url_id", return_value="MIT"), \
         mock.patch("src.update.osi_data_update.get_aliases", return_value=["MIT", "MIT License"]), \
         mock.patch("src.update.osi_data_update.update_data"), \
         mock.patch("src.update.osi_data_update.delete_file"):
        process_licenses()


def test_process_licenses_recognized(mock_logger):
    with mock.patch("src.update.osi_data_update.download_license_list_json"), \
         mock.patch("src.update.osi_data_update.load_json_file",
                    return_value=[{"id": "mit", "name": "MIT License"}]), \
         mock.patch("src.update.osi_data_update.extract_url_id", return_value="mit"), \
         mock.patch("src.update.osi_data_update.get_aliases", return_value=["MIT License"]), \
         mock.patch("src.update.osi_data_update.update_data"), \
         mock.patch("src.update.osi_data_update.delete_file"):
        process_licenses()


def test_process_licenses_unrecognized(mock_logger):
    with mock.patch("src.update.osi_data_update.download_license_list_json"), \
         mock.patch("src.update.osi_data_update.load_json_file",
                    return_value=[{"id": "Unknown License for testing", "name": "Unknown License for testing"}]), mock.patch("src.update"), \
         mock.patch("src.update.osi_data_update.extract_url_id", return_value="Unknown License for testing"), \
         mock.patch("src.update.osi_data_update.get_aliases", return_value=["Unknown License for testing"]), \
         mock.patch("src.update.osi_data_update.update_data"), \
         mock.patch("src.update.osi_data_update.delete_file"):
        process_licenses()
