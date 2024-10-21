import json

import pytest
from unittest.mock import mock_open, patch, MagicMock
from licenselynx.licenselynx import LicenseLynx, LicenseObject


@pytest.fixture
def mock_json_data():
    return '{"Academic Free License v2.1": {"canonical": "AFL-2.1","src": "spdx"}}'


def test_map_with_existing_license():
    mock_data = json.dumps({
        "MIT": {
            "canonical": "MIT License",
            "src": "opensource.org/licenses/MIT"
        }
    })
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        license_lynx = LicenseLynx()
        result = license_lynx.map("MIT")
        assert isinstance(result, LicenseObject)
        assert result.canonical == "MIT License"
        assert result.src == "opensource.org/licenses/MIT"


def test_map_with_non_existing_license():
    mock_data = json.dumps({})
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        license_lynx = LicenseLynx()
        result = license_lynx.map("GPL")
        assert result is None


def test_map_with_file_not_found_error():
    with patch('importlib.resources.files', side_effect=FileNotFoundError):
        license_lynx = LicenseLynx()
        result = license_lynx.map("MIT")
        assert result == {"error": "Error reading or parsing file: " + str(FileNotFoundError())}


if __name__ == '__main__':
    pytest.main()
