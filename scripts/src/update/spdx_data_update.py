import json
import os
import sys
import requests
from src.logger import setup_logger

logger = setup_logger(__name__, log_level=10)

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

sys.path.append(os.path.abspath(os.path.join(script_dir, '../../')))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def download_spdx_license_list(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        logger.debug("SPDX license list downloaded successfully.")
    else:
        logger.debug("Failed to download SPDX license list.")


def load_spdx_license_list(filepath):
    with open(filepath, 'r') as f:
        spdx_data = json.load(f)
    return spdx_data


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.debug(f"File '{filepath}' deleted successfully.")
    else:
        logger.debug(f"File '{filepath}' does not exist.")


def create_json(input_file, is_exception: bool = False):
    """
    Create a json file that contains SPDX license information
    Args:
        input_file: SPDX license list
        is_exception: boolean indicating if SPDX license list is the SPDX exception list or not
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    # Dictionary to keep track of deprecated license IDs; [0] is non-deprecated license path, [1] the deprecated one
    duplicate_aliases: dict[str, [str]] = {}

    # Dictionary to map canonical names to their corresponding filenames
    canonical_to_file: dict[str, str] = {}

    # Load existing files to build the canonical_to_file dictionary
    build_canonical_dictionary(canonical_to_file)

    # GNU Free Documentation License v1.1 to v1.3 are deprecated but their alias also changed
    # The 'only' addition does not exist in the deprecated version
    skip_licenses = ["GFDL-1.1", "GFDL-1.2", "GFDL-1.3"]

    with open(input_file, 'r') as f:
        data = json.load(f)
        if not is_exception:
            licenses = data.get("licenses", [])
        else:
            licenses = data.get("exceptions", [])

    for lic in licenses:
        if not is_exception:
            license_id = lic.get('licenseId')
        else:
            license_id = lic.get('licenseExceptionId')

        if license_id in skip_licenses:
            continue

        output_file = os.path.join(DATA_DIR, f"{license_id}.json")
        name = lic.get('name')

        is_deprecated = lic.get('isDeprecatedLicenseId')

        collect_duplicates(duplicate_aliases, is_deprecated, output_file, name)

        if not os.path.exists(output_file):
            logger.debug(f"Creating new data file: {output_file}")

            # Determine the aliases for the current license
            aliases = [name]

            output_data = {
                "canonical": license_id,
                "aliases": {
                    "spdx": aliases,
                    "custom": []
                },
                "src": "spdx"
            }

            # Write new data to the file
            with open(output_file, 'w') as outfile:
                json.dump(output_data, outfile, indent=4)
        else:
            logger.debug(f"License already exists: {output_file}")

            # Rename file if filename and canonical name are different now
            check_canonical_name_with_file(canonical_to_file, license_id, output_file)

    duplicate_aliases = {key: value for key, value in duplicate_aliases.items()
                         if isinstance(value, list) and len(value) >= 2}

    remove_duplicate_licenses(duplicate_aliases)


def remove_duplicate_licenses(duplicate_aliases):
    """
    Remove duplicate licenses
    Args:
        duplicate_aliases: Dictionary of duplicates
    """
    for alias, filepaths in duplicate_aliases.items():
        with open(filepaths[0], 'r') as f:
            data_not_deprecated = json.load(f)

        with open(filepaths[1], 'r') as f:
            data_deprecated = json.load(f)

        deprecated_spdx_id = data_deprecated['canonical']

        aliases_not_deprecated = data_not_deprecated['aliases']

        if aliases_not_deprecated not in aliases_not_deprecated['spdx']:
            aliases_not_deprecated['spdx'].append(deprecated_spdx_id)

        delete_file(filepaths[1])


def collect_duplicates(duplicate_aliases, is_deprecated, output_file, name):
    """
    Collects duplicate aliases and adds them to the duplicate_aliases dictionary
    Args:
        duplicate_aliases: duplicate_aliases dictionary
        is_deprecated: is_deprecated boolean
        output_file: file path of the license
        name: name of the license
    """
    if "GNU Free Documentation License v1.3 only" == name:
        print()
    if name not in duplicate_aliases:
        duplicate_aliases[name] = []
    if is_deprecated:
        duplicate_aliases[name].append(output_file)
    else:
        duplicate_aliases[name].insert(0, output_file)


def check_canonical_name_with_file(canonical_to_file, license_id, output_file):
    """
    Check for existing canonical name and rename file if canonical name changed and file name and

    Args:
        canonical_to_file: Mapping of canonical_name and filepath
        license_id:
        output_file:
    """
    logger.debug("Checking if canonical name and filename matches")
    if license_id in canonical_to_file:
        existing_path = canonical_to_file[license_id]
        if existing_path != output_file:
            logger.debug(f"Renaming {existing_path} to {output_file}")
            os.rename(existing_path, output_file)
            # Update the mapping
            canonical_to_file[license_id] = output_file


def build_canonical_dictionary(canonical_to_file):
    """
    Helper method to keep track of the mapping between canonical name and file path.
    Canonical_to_file is used later to check if the filename and the canonical name are the same.
    Args:
        canonical_to_file: Mapping of canonical_name and its filepath
    """
    existing_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    for existing_file in existing_files:
        existing_path = os.path.join(DATA_DIR, existing_file)
        with open(existing_path, 'r') as ef:
            existing_data = json.load(ef)
            canonical_name = existing_data.get("canonical")
            if canonical_name:
                canonical_to_file[canonical_name] = existing_path


def main():
    spdx_license_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    spdx_license_file = "spdx_license_list.json"

    spdx_exception_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json"
    spdx_exception_file = "spdx_exceptions.json"

    download_spdx_license_list(spdx_license_url, spdx_license_file)
    create_json(spdx_license_file, is_exception=False)

    delete_file(spdx_license_file)

    download_spdx_license_list(spdx_exception_url, spdx_exception_file)
    create_json(spdx_exception_file, is_exception=True)
    delete_file(spdx_exception_file)


if __name__ == "__main__":
    main()
