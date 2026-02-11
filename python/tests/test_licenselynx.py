#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
import pytest
from unittest.mock import mock_open, patch, MagicMock
from licenselynx.licenselynx import LicenseLynx
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import _LicenseMapSingleton

LICENSE_STRING_STABLE = "MIT License"
LICENSE_STRING_RISKY = "GPL License"
LICENSE_STRING_WITH_QUOTES = "‚MIT‛ License"
LICENSE_STRING_WITH_NORMALIZED_QUOTES = "'MIT' License"
LICENSE_STRING_SCANCODE = "Some License"
CANONICAL_ID_SCANCODE = "SOME"
CANONICAL_ID_STABLE = "MIT"
CANONICAL_ID_RISKY = "GPL"
SPDX_SRC = "spdx"
SCANCODE_SRC = "scancode-licensedb"


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Resets the singleton instance before each test."""
    monkeypatch.setattr(_LicenseMapSingleton, "_instances", {})


@pytest.fixture(autouse=True)
def mock_data():
    """Mocks the merged_data.json file for testing."""
    mock_data = {"stableMap": {LICENSE_STRING_STABLE: {"id": CANONICAL_ID_STABLE, "src": SPDX_SRC},
                               LICENSE_STRING_WITH_NORMALIZED_QUOTES: {"id": CANONICAL_ID_STABLE,
                                                                       "src": SPDX_SRC},
                               LICENSE_STRING_SCANCODE: {"id": CANONICAL_ID_STABLE, "src": SCANCODE_SRC},
                               },
                 "riskyMap": {LICENSE_STRING_RISKY: {"id": CANONICAL_ID_RISKY, "src": SPDX_SRC}}}
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=json.dumps(mock_data)).return_value

    with patch('importlib.resources.files') as mock_resources_files:
        mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
        yield


def test_license_map_singleton(mock_data):
    instance = _LicenseMapSingleton()

    instance2 = _LicenseMapSingleton()

    assert instance == instance2
    assert instance.merged_data.risky_map.get(LICENSE_STRING_RISKY).id == CANONICAL_ID_RISKY
    assert instance.merged_data.risky_map.get(LICENSE_STRING_RISKY).src == SPDX_SRC

    assert instance.merged_data.stable_map.get(LICENSE_STRING_STABLE).id == CANONICAL_ID_STABLE
    assert instance.merged_data.stable_map.get(LICENSE_STRING_STABLE).src == SPDX_SRC


def test_map_with_existing_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_STABLE)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_STABLE
    assert result.src == SPDX_SRC


def test_map_with_existing_risky_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_RISKY, risky=True)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_RISKY
    assert result.src == SPDX_SRC


def test_map_with_quotes_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_WITH_QUOTES, risky=True)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_STABLE
    assert result.src == SPDX_SRC


def test_map_with_non_existing_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_RISKY)
    result2 = LicenseLynx.map(CANONICAL_ID_RISKY, risky=True)
    assert result is None
    assert result2 is None


def test_is_spdx_identifier(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_STABLE)

    assert result.is_spdx_identifier() is True

def test_is_scancode_licensedb_identifier(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_SCANCODE)

    assert result.is_scancode_licensedb_identifier() is True

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
        {"stableMap": {CANONICAL_ID_STABLE: {"id": LICENSE_STRING_STABLE}}, "riskyMap": {}})  # Missing 'src' key
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data).return_value
    with pytest.raises(Exception) as exit_code:
        with patch('importlib.resources.files') as mock_resources_files:
            mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
            LicenseLynx.map(CANONICAL_ID_STABLE)
    assert exit_code.type == TypeError


def test_init_with_generic_exception():
    with patch('importlib.resources.files', side_effect=Exception("Generic error")):
        with pytest.raises(Exception) as e:
            LicenseLynx.map("")
        assert str(e.value) == "Generic error"


if __name__ == '__main__':
    pytest.main()
