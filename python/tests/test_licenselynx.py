#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: Apache-2.0
#
import json
import pytest
from unittest.mock import mock_open, patch, MagicMock
from licenselynx.licenselynx import LicenseLynx
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import _LicenseMapSingleton


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Resets the singleton instance before each test."""
    monkeypatch.setattr(_LicenseMapSingleton, "_instances", {})


def test_license_map_singleton():
    mock_data = {"stable_map": {"MIT": {"canonical": "MIT License", "src": "spdx"}},
                 "risky_map": {"MIT2": {"canonical": "MIT License", "src": "spdx"}}}

    with patch('importlib.resources.files') as mock_resources_files:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_open(read_data=json.dumps(mock_data)).return_value
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file

        instance = _LicenseMapSingleton()

        instance2 = _LicenseMapSingleton()

        assert instance == instance2
        assert instance.merged_data.risky_map.get("MIT2").canonical == "MIT License"
        assert instance.merged_data.risky_map.get("MIT2").src == "spdx"

        assert instance.merged_data.stable_map.get("MIT").canonical == "MIT License"
        assert instance.merged_data.stable_map.get("MIT").src == "spdx"


def test_map_with_existing_license():
    mock_data = json.dumps({"stable_map": {"MIT": {"canonical": "MIT License", "src": "spdx"}}, "risky_map": {}})
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        result = LicenseLynx.map("MIT")

        assert isinstance(result, LicenseObject)
        assert result.canonical == "MIT License"
        assert result.src == "spdx"


def test_map_with_existing_risky_license():
    mock_data = json.dumps({"stable_map": {"MIT2": {"canonical": "MIT License", "src": "spdx"}},
                            "risky_map": {"MIT": {"canonical": "MIT License", "src": "spdx"}}})
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        result = LicenseLynx.map("MIT", risky=True)

        assert isinstance(result, LicenseObject)
        assert result.canonical == "MIT License"
        assert result.src == "spdx"


def test_map_with_non_existing_license():
    mock_data = json.dumps({"stable_map": {"MIT": {"canonical": "MIT License", "src": "spdx"}}, "risky_map": {}})
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        result = LicenseLynx.map("GPL")
        result2 = LicenseLynx.map("GPL", risky=True)
        assert result is None
        assert result2 is None


def test_map_with_file_not_found_error():
    with patch('importlib.resources.files', side_effect=FileNotFoundError):
        with pytest.raises(Exception) as e:
            _LicenseMapSingleton()
        assert e.type == FileNotFoundError


def test_init_with_json_decode_error():
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data="invalid json").return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        with pytest.raises(json.JSONDecodeError):
            _LicenseMapSingleton()


def test_map_with_type_error():
    mock_data = json.dumps(
        {"stable_map": {"MIT": {"canonical": "MIT License"}}, "risky_map": {}})  # Missing 'src' key
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value
    with pytest.raises(Exception) as exit_code:
        with patch('importlib.resources.files') as mock_resources_files:
            mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
            LicenseLynx.map("MIT")
    assert exit_code.type == TypeError


def test_init_with_generic_exception():
    with patch('importlib.resources.files', side_effect=Exception("Generic error")):
        with pytest.raises(Exception) as e:
            LicenseLynx.map("")
        assert str(e.value) == "Generic error"


if __name__ == '__main__':
    pytest.main()
