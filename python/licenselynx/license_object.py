#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import dataclass


@dataclass
class LicenseObject(object):
    canonical: str
    src: str
