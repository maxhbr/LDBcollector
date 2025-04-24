#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: Apache-2.0
#
import json
import sys
from importlib import resources
from threading import Lock


class Singleton(type):
    _instances: dict[type, type] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class LicenseMapSingleton(metaclass=Singleton):
    def __init__(self):
        self._file_path = resources.files("licenselynx.resources").joinpath("merged_data.json")
        try:
            with self._file_path.open() as file:
                self._merged_data = json.load(file)
        except Exception as e:
            raise e.with_traceback(sys.exc_info()[2])

    @property
    def merged_data(self) -> dict:
        return self._merged_data
