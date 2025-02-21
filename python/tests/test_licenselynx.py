#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import pytest
from unittest.mock import mock_open, patch, MagicMock
from licenselynx.licenselynx import LicenseLynx
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import LicenseMapSingleton


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Resets the singleton instance before each test."""
    monkeypatch.setattr(LicenseMapSingleton, "_instances", {})


def test_license_map_singleton():
    mock_data = {"MIT": {"canonical": "MIT License", "src": "opensource.org/licenses/MIT"}}

    with patch('importlib.resources.files') as mock_resources_files:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_open(read_data=json.dumps(mock_data)).return_value
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file

        instance = LicenseMapSingleton()

        instance2 = LicenseMapSingleton()

        assert instance == instance2


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
        result = LicenseLynx.map("MIT")

        assert isinstance(result, LicenseObject)
        assert result.canonical == "MIT License"
        assert result.src == "opensource.org/licenses/MIT"


def test_map_with_non_existing_license():
    mock_data = json.dumps({})
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        result = LicenseLynx.map("GPL")
        assert result is None


def test_map_with_file_not_found_error():
    with patch('importlib.resources.files', side_effect=FileNotFoundError):
        with pytest.raises(Exception) as e:
            LicenseMapSingleton()
        assert e.type == FileNotFoundError


def test_init_with_json_decode_error():
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data="invalid json").return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        with pytest.raises(json.JSONDecodeError):
            LicenseMapSingleton()


def test_map_with_key_error():
    mock_data = json.dumps({"MIT": {"canonical": "MIT License"}})  # Missing 'src' key
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        result = LicenseLynx.map("MIT")
        assert result is not None
        assert result.canonical == "MIT License"
        assert result.src is None  # Should handle missing 'src' gracefully


def test_map_with_runtime_error():
    mock_data = {"MIT": {"canonical": "MIT License", "src": "opensource.org/licenses/MIT"}}

    with patch('importlib.resources.files') as mock_resources_files:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_open(read_data=json.dumps(mock_data)).return_value
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file

        instance = LicenseMapSingleton()

    with patch.object(instance, '_merged_data', create=True) as mock_merged_data:
        mock_merged_data.get.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(RuntimeError) as e:
            LicenseLynx.map("MIT")

        assert str(e.value) == "Unexpected error"


def test_init_with_generic_exception():
    with patch('importlib.resources.files', side_effect=Exception("Generic error")):
        with pytest.raises(Exception) as e:
            LicenseLynx.map("")
        assert str(e.value) == "Generic error"


if __name__ == '__main__':
    pytest.main()
