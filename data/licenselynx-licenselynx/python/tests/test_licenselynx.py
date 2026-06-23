#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
from enum import StrEnum
from unittest.mock import mock_open, patch, MagicMock

import pytest
import licenselynx.license_map_singleton as license_map_singleton_module
import licenselynx.license_object as license_object_module
from licenselynx.licenselynx import LicenseLynx
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import _LicenseMapSingleton
from licenselynx.license_source import LicenseSource

LICENSE_STRING_STABLE = "MIT License"
LICENSE_STRING_RISKY = "GPL License"
LICENSE_STRING_WITH_QUOTES = "\u201AMIT\u201B License"
LICENSE_STRING_WITH_NORMALIZED_QUOTES = "'MIT' License"
LICENSE_STRING_SCANCODE = "Some License"
CANONICAL_ID_SCANCODE = "SOME"
CANONICAL_ID_STABLE = "MIT"
CANONICAL_ID_RISKY = "GPL"
LICENSE_STRING_ORG = "testOrg"
CANONICAL_ID_ORG = "testOrgId"


class TestOrganization(StrEnum):
    TEST_ORG = "testOrg"


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch):
    """Resets the singleton instance before each test."""
    monkeypatch.setattr(_LicenseMapSingleton, "_instances", {})


@pytest.fixture(autouse=True)
def mock_organization(monkeypatch):
    monkeypatch.setattr(license_map_singleton_module, "Organization", TestOrganization)
    monkeypatch.setattr(license_object_module, "Organization", TestOrganization)


@pytest.fixture(autouse=True)
def mock_data():
    """Mocks the merged_data.json file for testing."""
    mock_data = {"stableMap": {LICENSE_STRING_STABLE: {"id": CANONICAL_ID_STABLE, "src": LicenseSource.SPDX.value},
                               LICENSE_STRING_WITH_NORMALIZED_QUOTES: {"id": CANONICAL_ID_STABLE,
                                                                       "src": LicenseSource.SPDX.value},
                               LICENSE_STRING_SCANCODE: {"id": CANONICAL_ID_STABLE, "src": LicenseSource.SCANCODE_LICENSEDB.value},
                               },
                 "riskyMap": {LICENSE_STRING_RISKY: {"id": CANONICAL_ID_RISKY, "src": LicenseSource.CUSTOM.value}},
                 TestOrganization.TEST_ORG: {LICENSE_STRING_ORG: {"id": CANONICAL_ID_ORG,
                                                                  "src": TestOrganization.TEST_ORG.value}}}
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
    assert instance.merged_data.risky_map.get(LICENSE_STRING_RISKY).src == LicenseSource.CUSTOM

    assert instance.merged_data.stable_map.get(LICENSE_STRING_STABLE).id == CANONICAL_ID_STABLE
    assert instance.merged_data.stable_map.get(LICENSE_STRING_STABLE).src == LicenseSource.SPDX


def test_map_with_existing_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_STABLE)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_STABLE
    assert result.src == LicenseSource.SPDX


def test_map_with_existing_risky_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_RISKY, risky=True)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_RISKY
    assert result.src == LicenseSource.CUSTOM


def test_map_with_quotes_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_WITH_QUOTES, risky=True)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_STABLE
    assert result.src == LicenseSource.SPDX


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


def test_is_custom_identifier(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_RISKY, risky=True)

    assert result.is_custom_identifier() is True


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
        {
            "stableMap": {CANONICAL_ID_STABLE: {"id": LICENSE_STRING_STABLE}},
            "riskyMap": {},
            TestOrganization.TEST_ORG: {},
        }
    )  # Missing 'src' key
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


def test_init_with_missing_org_in_data():
    """Tests that a ValueError is raised when an Organization enum value is missing from merged_data.json."""
    mock_data_missing_org = json.dumps(
        {"stableMap": {}, "riskyMap": {}}  # Missing "testOrg" key
    )
    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_open(read_data=mock_data_missing_org).return_value
    with pytest.raises(ValueError, match="Organization 'testOrg' is defined in the Organization enum but missing from merged_data.json"):
        with patch('importlib.resources.files') as mock_resources_files:
            mock_resources_files.return_value.joinpath.return_value.open.return_value = mock_file
            _LicenseMapSingleton()


def test_map_with_org_license(mock_data):
    result = LicenseLynx.map(LICENSE_STRING_ORG, org=TestOrganization.TEST_ORG)

    assert isinstance(result, LicenseObject)
    assert result.id == CANONICAL_ID_ORG
    assert result.src == TestOrganization.TEST_ORG.value


def test_is_organization_source(mock_data):
    org_result = LicenseLynx.map(LICENSE_STRING_ORG, org=TestOrganization.TEST_ORG)
    non_org_result = LicenseLynx.map(LICENSE_STRING_STABLE)

    assert org_result.is_organization_source() is True
    assert non_org_result.is_organization_source() is False


def test_is_organization_source_of(mock_data):
    org_result = LicenseLynx.map(LICENSE_STRING_ORG, org=TestOrganization.TEST_ORG)
    non_org_result = LicenseLynx.map(LICENSE_STRING_STABLE)

    assert org_result.is_organization_source_of(TestOrganization.TEST_ORG) is True
    assert non_org_result.is_organization_source_of(TestOrganization.TEST_ORG) is False


if __name__ == '__main__':
    pytest.main()
