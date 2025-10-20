#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import sys
from typing import Optional
from licenselynx.license_object import LicenseObject
from licenselynx.license_map_singleton import _LicenseMapSingleton
from licenselynx.quotes_handler import _QuotesHandler


class LicenseLynx:

    @staticmethod
    def map(license_name: str, risky: bool = False) -> Optional[LicenseObject]:
        """
        Maps license name to the canonical license identifier
        :param license_name: string of a license name
        :param risky: enable risky mappings
        :return: LicenseObject with the canonical license identifier and source, None if no license is found,
        or throws an exception if a runtime error occurs
        """
        try:
            license_name = _QuotesHandler().normalize_quotes(license_name)
            instance = _LicenseMapSingleton()

            license_object: Optional[LicenseObject] = instance.merged_data.stable_map.get(license_name)

            if not license_object and risky:
                license_object = instance.merged_data.risky_map.get(license_name)

            if not license_object:
                return None

            return license_object
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])
