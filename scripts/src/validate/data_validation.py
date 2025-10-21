#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import os
from enum import Enum
import re

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


def extract_license_list_with_semver(licenses_list):
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                canonical = data["canonical"]["id"]

                canonical_tokens = extract_version_tokens(canonical)
                canonical_has_version = bool(canonical_tokens)
                if canonical_has_version:
                    canonical_and_version = (canonical, canonical_tokens)
                    licenses_list.append(canonical_and_version)


def build_dict_with_base_name_license(licenses_list):
    base_name_dict = {}
    for name, version_set in licenses_list:
        if len(version_set) > 1:
            continue
        (version,) = version_set
        base_name = name.replace(version, '')
        if base_name not in base_name_dict:
            base_name_dict[base_name] = [(name, int(version.split(".")[0]))]
        else:
            base_name_dict[base_name].append((name, int(version.split(".")[0])))

    return base_name_dict


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
                canonical_id = data["canonical"]["id"]
                if canonical_id != filename[:-5]:
                    logger.error(f"JSON filename '{filename}' does not match canonical id '{canonical_id}'")
        else:
            logger.error(f"File '{filename}' is not a JSON file.")


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
        filepath = os.path.join(DATA_DIR, filename)
        with (open(filepath, 'r') as f):
            data = json.load(f)
            canonical_name = data["canonical"]["id"]
            if (canonical_name in spdx_license_list or canonical_name in spdx_exception_list) and data["canonical"]["src"] != "spdx":
                logger.error(f"If src is SPDX, canonical name '{canonical_name}' must be in SPDX license list")
            elif (canonical_name not in spdx_license_list and
                  canonical_name not in spdx_exception_list) and data["canonical"]["src"] == "spdx":
                logger.error(f"Canonical name '{canonical_name}' is in SPDX license list but source is not 'spdx'.")


def check_length_and_characters():
    forbidden_characters_canonical = {"#", "$", "%", "=", "[", "]", "?", "<", ">", ":", "/", "\\", "|", "*", " "}

    max_length = 100  # Adjust the maximum length limit as needed
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            canonical_id = data["canonical"]["id"]
            aliases = data.get("aliases")
            aliases = flatten_aliases_dict(aliases)
            src = data["canonical"]["src"]

            # Max length check
            if len(canonical_id) > max_length:
                logger.error(f"Canonical id '{canonical_id}' "
                             f"exceeds maximum length limit of {max_length} characters")
            if any(len(alias) > max_length for alias in aliases):
                logger.error(f"At least one of the aliases exceeds maximum length limit of {max_length} characters "
                             f"in the file {filename}")
            if len(src) > max_length:
                logger.error(f"Source {src} exceeds maximum length limit of {max_length} characters")

            # Forbidden char check
            if any(char in forbidden_characters_canonical for char in canonical_id):
                logger.error(f"Canonical id '{canonical_id}' contains forbidden characters")


def check_no_empty_field_except_custom():
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)

            if not data["canonical"]["id"]:
                logger.error(f"Field 'canonical.id' in '{filename}' is empty.")
            if not data["aliases"]:
                logger.error(f"Field 'aliases' in '{filename}' is empty.")
            for key, value in data["aliases"].items():
                if not value and key != "custom":
                    logger.error(f"Alias list in '{filename}' for field '{key}' is empty.")
            if not data["canonical"]["src"]:
                logger.error(f"Field 'canonical.src' in '{filename}' is empty.")


def check_rejected_field_exists():
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            if "rejected" not in data:
                logger.error(f"rejected field '{filename}' does not exist.")


def check_rejected_not_in_valid_fields():
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            aliases = data.get("aliases", [])
            aliases_list = flatten_aliases_dict(aliases)
            rejected = data.get("rejected", [])
            matched = set(aliases_list) & set(rejected)
            if matched:
                logger.error(f"rejected aliases {matched} in '{filename}' is in aliases list")


def flatten_aliases_dict(aliases_dict):
    aliases_list = []
    for src, aliases in aliases_dict.items():
        aliases_list += aliases
    return aliases_list


def extract_version_tokens(identifier) -> set:
    """
    Extracts version tokens from an identifier.
    It looks for tokens that are either numeric or are recognized digit words.
    """
    token_pattern = re.compile(r'(\d+\.\d+(?:\.\d+)*)', re.IGNORECASE)
    version_tokens = set(token_pattern.findall(identifier))
    return version_tokens


def check_version_between_canonical_and_alias():
    affected_licenses = {}
    licenses_with_version = []
    extract_license_list_with_semver(licenses_with_version)
    base_name_license_dict = build_dict_with_base_name_license(licenses_with_version)

    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            aliases = data.get("aliases", [])

            custom_aliases = aliases.pop('custom')
            aliases_list = custom_aliases
            for alias_src, alias_list in aliases.items():
                if alias_src == 'spdx' or alias_src == 'osi':
                    continue
                aliases_list += alias_list
            canonical_id = data["canonical"]["id"]

            is_major_version_only = data.get("isMajorVersionOnly")

            wrong_version = []

            canonical_tokens = extract_version_tokens(canonical_id)

            canonical_has_version = bool(canonical_tokens)
            if canonical_has_version:
                compare_versions(aliases_list, canonical_tokens, wrong_version, is_major_version_only, canonical_id, base_name_license_dict)
            if wrong_version:
                wrong_version.sort()
                logger.error(f'{filename} has wrong versions for aliases: {wrong_version}')
                affected_licenses[canonical_id] = wrong_version


def get_base_name_number(canonical_id, base_name_license_dict) -> bool:
    for base_name, licenses in base_name_license_dict.items():
        if len(licenses) == 1:
            if canonical_id == licenses[0][0]:
                return True
    return False


def compare_versions(aliases_list, canonical_tokens, wrong_version, is_major_version_only, canonical_id, base_name_license_dict):
    for alias in aliases_list:
        alias_tokens = extract_version_tokens(alias)
        if alias_tokens != canonical_tokens:
            if len(canonical_tokens) == 1 and is_major_version_only:
                major_str = list(canonical_tokens).pop().split('.')[0]
                numbers_found = re.findall(r'\d+', alias)
                if numbers_found and all(num == major_str for num in numbers_found):
                    continue
            is_only_base_name = get_base_name_number(canonical_id, base_name_license_dict)
            if is_only_base_name and is_major_version_only:
                continue

            wrong_version.append(alias)


def check_major_version_flag():
    """
    Validates that for each JSON file in DATA_DIR with a canonical name containing a single version token
    (e.g. "Apache-2.0"), the 'isMajorVersionOnly' flag has been set correctly.

    For each group of licenses (grouped by base name, i.e. canonical with the version removed) that contains more than one file,
    if a license’s major version occurs only once then its expected 'isMajorVersionOnly' flag is True.
    Otherwise (if the major version appears for more than one file) the flag should be False.

    Files that do not have a semver in the canonical field or that belong to a group of one are skipped.
    """
    group_by_base = group_license_files_by_base_name()

    # Now, for each group with more than one file, perform the check
    for base, files in group_by_base.items():

        # Determine if a major version number appears more than once for the group
        major_versions = [info["major"] for info in files]
        duplicate_majors = {maj for maj in major_versions if major_versions.count(maj) > 1}
        # Check each file in the group
        for info in files:
            # Expected flag is True if its major version number is unique, else False.
            expected_flag = True if info["major"] not in duplicate_majors else False
            if info["flag"] != expected_flag:
                logger.error(
                    f"File '{info['filename']}' has 'isMajorVersionOnly'={info['flag']} but "
                    f"expected {expected_flag} based on canonical '{info['canonical']}'"
                )


def group_license_files_by_base_name():
    group_by_base = {}
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file {filename}")
            continue

        canonical_id = data["canonical"]["id"]
        if not canonical_id:
            continue

        canonical_tokens = extract_version_tokens(canonical_id)
        # Process only if exactly one version token is found
        if len(canonical_tokens) != 1:
            continue

        version = next(iter(canonical_tokens))
        base_name = canonical_id.replace(version, '')
        try:
            major = int(version.split('.')[0])
        except ValueError:
            logger.error(f"Invalid version format in file {filename}: {version}")
            continue

        file_info = {
            "filename": filename,
            "canonical": canonical_id,
            "major": major,
            "flag": data.get("isMajorVersionOnly")
        }
        group_by_base.setdefault(base_name, []).append(file_info)
    return group_by_base


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

    check_rejected_field_exists()
    check_rejected_not_in_valid_fields()

    delete_file(spdx_license_file)
    delete_file(spdx_exception_file)
    delete_file(scancode_licensedb_file)

    check_json_filename()
    check_unique_aliases()
    check_length_and_characters()

    check_no_empty_field_except_custom()

    check_version_between_canonical_and_alias()
    check_major_version_flag()
    # Check if error occurred
    if logger.handlers[1].error_occurred:
        exit(1)


if __name__ == "__main__":
    main()
