import json

import pytest
from unittest.mock import mock_open, patch
from licenselynx.licenselynx import LicenseLynx


@pytest.fixture
def mock_json_data():
    return '{"Academic Free License v2.1": {"canonical": "AFL-2.1","src": "spdx"}}'


def test_map_with_existing_license(mock_json_data):
    with patch('builtins.open', mock_open(read_data=mock_json_data)):
        license_lynx = LicenseLynx()
        result = license_lynx.map("Academic Free License v2.1")
        assert result.canonical == "AFL-2.1"
        assert result.src == "spdx"


def test_map_with_non_existing_license():
    mock_data = json.dumps({})
    with patch('importlib.resources.open_text', mock_open(read_data=mock_data)):
        license_lynx = LicenseLynx()
        result = license_lynx.map("GPL")
        assert result is None


def test_map_with_file_not_found_error():
    with patch('importlib.resources.open_text', side_effect=FileNotFoundError):
        license_lynx = LicenseLynx()
        result = license_lynx.map("MIT")
        assert result == {"error": "Error reading or parsing file: " + str(FileNotFoundError())}


if __name__ == '__main__':
    pytest.main()
