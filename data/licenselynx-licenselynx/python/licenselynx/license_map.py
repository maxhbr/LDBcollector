#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
from dataclasses import dataclass

from licenselynx.license_object import LicenseObject
from licenselynx.organization import Organization


@dataclass
class _LicenseMap(object):
    stable_map: dict[str, LicenseObject]
    risky_map: dict[str, LicenseObject]
    organizations: dict[Organization, dict[str, LicenseObject]]
