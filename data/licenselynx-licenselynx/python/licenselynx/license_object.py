#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
from dataclasses import dataclass


@dataclass
class LicenseObject(object):
    id: str
    src: str
