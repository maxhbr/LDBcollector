import json
import sys
from importlib import resources
from typing import Optional
from licenselynx.license_object import LicenseObject


class LicenseLynx:
    def __init__(self):
        self._file_path = resources.files("licenselynx.resources").joinpath("merged_data.json")
        try:
            with self._file_path.open() as file:
                self._merged_data = json.load(file)
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

    def map(self, license_name: str) -> Optional[LicenseObject]:
        """
        Maps license name to the canonical license identifier
        :param license_name: string of a license name
        :return: LicenseObject with the canonical license identifier and source, None if no license is found,
        or throws an exception if a runtime error occurs
        """
        try:
            entry = self._merged_data.get(license_name, None)

            if not entry:
                return None

            return LicenseObject(canonical=entry.get("canonical"), src=entry.get("src"))
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])
