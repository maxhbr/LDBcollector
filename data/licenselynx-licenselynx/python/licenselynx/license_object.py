#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
from dataclasses import dataclass

from licenselynx.license_source import LicenseSource
from licenselynx.organization import Organization


@dataclass
class LicenseObject(object):
    """LicenseObject class represents a license with a canonical name and source."""

    id: str
    src: str

    def is_spdx_identifier(self):
        """
        Checks if source of LicenseObject is SPDX.
        :return: True if source of LicenseObject is SPDX
        """
        return self.src == LicenseSource.SPDX

    def is_scancode_licensedb_identifier(self):
        """
        Checks if source of LicenseObject is ScanCode LicenseDB.
        :return: True if source of LicenseObject is ScanCode LicenseDB
        """
        return self.src == LicenseSource.SCANCODE_LICENSEDB

    def is_custom_identifier(self):
        """
        Checks if source of LicenseObject is custom.
        :return: True if source of LicenseObject is custom
        """
        return self.src == LicenseSource.CUSTOM

    def is_organization_source(self) -> bool:
        """
        Checks if source of LicenseObject is any organization.
        :return: True if source of LicenseObject is an Organization
        """
        return self.src in [org.value for org in Organization]

    def is_organization_source_of(self, org: Organization) -> bool:
        """
        Checks if source of LicenseObject is a specific organization.
        :param org: Organization enum value to check against
        :return: True if source matches the given organization
        """
        return self.src == org
