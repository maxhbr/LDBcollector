#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import os
from enum import Enum

import requests
from src.logger import setup_logger

script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))
JSON_EXTENSION = ".json"

logger = setup_logger(__name__)


class LicenseListType(Enum):
    SPDX = 1
    SPDX_EXCEPTION = 2
    SCANCODE_LICENSEDB = 3


def download_license_list(url: str, output_file: str, license_list_name: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        logger.info(f"{license_list_name} downloaded successfully.")
    else:
        logger.error(f"Failed to download {license_list_name}.")


def load_ids_from_license_list(filepath: str, license_list_type: LicenseListType) -> list[str]:
    with open(filepath, 'r') as f:
        data = json.load(f)
    license_ids = []
    if license_list_type is LicenseListType.SPDX:
        licenses = data.get("licenses", [])
        license_ids = [lic.get("licenseId") for lic in licenses]

    elif license_list_type is LicenseListType.SPDX_EXCEPTION:
        licenses = data.get("exceptions", [])
        license_ids = [lic.get("licenseExceptionId") for lic in licenses]

    elif license_list_type is LicenseListType.SCANCODE_LICENSEDB:
        for lic in data:
            if "spdx_license_key" in lic and lic["spdx_license_key"] is not None:
                spdx_id = lic["spdx_license_key"]
                if not spdx_id.startswith("LicenseRef"):
                    license_ids.append(spdx_id)
                else:
                    license_ids.append(lic.get("license_key"))
            else:
                license_ids.append(lic.get("license_key"))

    return license_ids


def delete_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"File '{filepath}' deleted successfully.")
    else:
        logger.error(f"File '{filepath}' does not exist.")


def check_json_filename():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(JSON_EXTENSION):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                canonical_name = data.get("canonical")
                if canonical_name != filename[:-5]:
                    logger.error(f"JSON filename '{filename}' does not match canonical name '{canonical_name}'")


def check_unique_aliases():
    all_aliases = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                aliases = data.get("aliases", [])
                access_aliases(aliases, all_aliases, filename)

    for alias, filenames in all_aliases.items():
        if len(filenames) > 1:
            logger.error(f"Alias '{alias}' is not unique globally. Affected file: {filenames}")


def access_aliases(aliases: dict, all_aliases: dict, filename: str):
    for alias in aliases:
        source = aliases[alias]
        for license_name in source:
            if license_name in all_aliases:
                all_aliases[license_name].append(filename)
            else:
                all_aliases[license_name] = [filename]


def check_src_and_canonical(spdx_license_list: list, spdx_exception_list: list):
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(JSON_EXTENSION):
            filepath = os.path.join(DATA_DIR, filename)
            with (open(filepath, 'r') as f):
                data = json.load(f)
                canonical_name = data.get("canonical")
                if (canonical_name in spdx_license_list or canonical_name in spdx_exception_list) and data["src"] != "spdx":
                    logger.error(f"If src is SPDX, canonical name '{canonical_name}' must be in SPDX license list")
                elif (canonical_name not in spdx_license_list and
                      canonical_name not in spdx_exception_list) and data["src"] == "spdx":
                    logger.error(f"Canonical name '{canonical_name}' is in SPDX license list but source is not 'spdx'.")


def check_length_and_characters():
    forbidden_characters_canonical = {"#", "$", "%", "=", "[", "]", "?", "<", ">", ":", "/", "\\", "|", "*", " "}

    max_length = 100  # Adjust the maximum length limit as needed
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(JSON_EXTENSION):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                canonical_name = data.get("canonical")
                aliases = data.get("aliases")
                src = data.get("src")

                # Max length check
                if len(canonical_name) > max_length:
                    logger.error(f"Canonical name '{canonical_name}' "
                                 f"exceeds maximum length limit of {max_length} characters")
                if any(len(alias) > max_length for alias in aliases):
                    logger.error(f"At least one of the aliases exceeds maximum length limit of {max_length} characters "
                                 f"in the file {filename}")
                if len(src) > max_length:
                    logger.error(f"Source {src} exceeds maximum length limit of {max_length} characters")

                # Forbidden char check
                if any(char in forbidden_characters_canonical for char in canonical_name):
                    logger.error(f"Canonical name '{canonical_name}' contains forbidden characters")


def check_no_empty_field_except_custom():
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)

            if not data["canonical"]:
                logger.error(f"Field 'canonical' in '{filename}' is empty.")
            if not data["aliases"]:
                logger.error(f"Field 'aliases' in '{filename}' is empty.")
            for key, value in data["aliases"].items():
                if not value and key != "custom":
                    logger.error(f"Alias list in '{filename}' for field '{key}' is empty.")
            if not data["src"]:
                logger.error(f"Field 'src' in '{filename}' is empty.")


def main():
    spdx_license_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    spdx_license_file = "spdx_license_list.json"

    spdx_exception_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json"
    spdx_exception_file = "spdx_exceptions.json"

    scancode_licensedb_url = "https://scancode-licensedb.aboutcode.org/index.json"
    scancode_licensedb_file = "licensedb_index.json"

    download_license_list(spdx_license_url, spdx_license_file, "SPDX license list")
    spdx_licenses = load_ids_from_license_list(spdx_license_file, LicenseListType.SPDX)

    download_license_list(spdx_exception_url, spdx_exception_file, "SPDX exception list")
    spdx_exception = load_ids_from_license_list(spdx_exception_file, LicenseListType.SPDX_EXCEPTION)

    download_license_list(scancode_licensedb_url, scancode_licensedb_file, "ScanCode LicenseDB license list")

    check_src_and_canonical(spdx_licenses, spdx_exception)
    delete_file(spdx_license_file)
    delete_file(spdx_exception_file)
    delete_file(scancode_licensedb_file)

    check_json_filename()
    check_unique_aliases()
    check_length_and_characters()

    check_no_empty_field_except_custom()
    # Check if error occurred
    if logger.handlers[1].error_occurred:
        exit(1)


if __name__ == "__main__":
    main()
