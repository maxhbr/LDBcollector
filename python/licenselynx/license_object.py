#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
from dataclasses import dataclass
from licenselynx.license_source import LicenseSource


@dataclass
class LicenseObject(object):
    """LicenseObject class represents a license with a canonical name and source."""

    id: str
    src: LicenseSource

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
