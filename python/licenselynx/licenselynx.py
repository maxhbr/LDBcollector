#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: Apache-2.0
#
import sys
from typing import Optional
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import LicenseMapSingleton


class LicenseLynx:

    @staticmethod
    def map(license_name: str) -> Optional[LicenseObject]:
        """
        Maps license name to the canonical license identifier
        :param license_name: string of a license name
        :return: LicenseObject with the canonical license identifier and source, None if no license is found,
        or throws an exception if a runtime error occurs
        """
        try:

            instance = LicenseMapSingleton()

            entry = instance.merged_data.get(license_name, None)

            if not entry:
                return None

            return LicenseObject(canonical=entry.get("canonical"), src=entry.get("src"))
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])
