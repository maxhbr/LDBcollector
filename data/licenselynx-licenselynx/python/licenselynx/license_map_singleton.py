#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
import json
import sys
from importlib import resources
from threading import Lock
from licenselynx.license_map import _LicenseMap
from licenselynx.license_object import LicenseObject
from licenselynx.organization import Organization


class _Singleton(type):
    _instances: dict[type, type] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class _LicenseMapSingleton(metaclass=_Singleton):
    def __init__(self):
        self._stable_map_str = "stableMap"
        self._risky_map_str = "riskyMap"
        self._file_path = resources.files("licenselynx.resources").joinpath("merged_data.json")
        try:
            with self._file_path.open() as file:
                data = json.load(file)

                stable_map = {}
                for key, value in data[self._stable_map_str].items():
                    stable_map[key] = LicenseObject(**value)
                risky_map = {}
                for key, value in data[self._risky_map_str].items():
                    risky_map[key] = LicenseObject(**value)

                orgs = self._add_orgs(data)

                self._merged_data = _LicenseMap(stable_map, risky_map, orgs)
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

    @staticmethod
    def _add_orgs(data) -> dict[Organization, dict[str, LicenseObject]]:
        orgs: dict[Organization, dict[str, LicenseObject]] = {}
        for org in Organization:
            if org not in data:
                raise ValueError(
                    f"Organization '{org}' is defined in the Organization enum "
                    f"but missing from merged_data.json. "
                    f"Available keys: {list(data.keys())}"
                )
            org_map: dict[str, LicenseObject] = {}
            for key, value in data[org].items():
                org_map[key] = LicenseObject(**value)
            orgs[org] = org_map
        return orgs

    @property
    def merged_data(self) -> _LicenseMap:
        return self._merged_data
