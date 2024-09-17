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

DATASOURCE_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


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


def process_json(input_file, is_exception: bool = False):
    os.makedirs(DATASOURCE_DIR, exist_ok=True)

    # Set to keep track of all aliases encountered
    encountered_aliases: set[str] = set()

    # Dictionary to keep track of deprecated license IDs
    deprecated_license_ids: dict[str, str] = {}

    # Dictionary to map canonical names to their corresponding filenames
    canonical_to_file: dict[str, str] = {}

    # Load existing files to build the canonical_to_file dictionary
    build_canonical_dictionary(canonical_to_file, DATASOURCE_DIR)

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

        output_file = os.path.join(DATASOURCE_DIR, f"{license_id}.json")

        if not os.path.exists(output_file):
            logger.debug(f"Create new data file: {output_file}")
            name = lic.get('name')

            is_deprecated = lic.get('isDeprecatedLicenseId')

            # Determine the aliases for the current license
            aliases = check_unique_alias(encountered_aliases, deprecated_license_ids, name, is_deprecated,
                                         license_id)

            # To prevent deprecated licenses getting dumped into a json file
            if aliases == "deprecated":
                continue

            output_data = {
                "canonical": license_id,
                "aliases": {
                    "spdx": aliases,
                    "custom": []
                },
                "src": "spdx"
            }

            # Check for existing canonical name and rename file if necessary
            check_canonical_name_with_file(canonical_to_file, license_id, output_file)

            # Write new data to the file if it does not exist or has different content
            with open(output_file, 'w') as outfile:
                json.dump(output_data, outfile, indent=4)


def check_canonical_name_with_file(canonical_to_file, license_id, new_output_file):
    if license_id in canonical_to_file:
        existing_path = canonical_to_file[license_id]
        if existing_path != new_output_file:
            os.rename(existing_path, new_output_file)
            # Update the mapping
            canonical_to_file[license_id] = new_output_file


def check_unique_alias(encountered_aliases, deprecated_license_ids, name, is_deprecated, license_id):
    aliases = []
    if name in encountered_aliases:
        if is_deprecated:
            aliases = "deprecated"
        else:
            deprecated_license_id = deprecated_license_ids[name]
            aliases.append(name)
            aliases.append(deprecated_license_id)

            deprecated_file_path = DATASOURCE_DIR + "/" + deprecated_license_id + ".json"
            delete_file(deprecated_file_path)
    else:
        aliases = [name]
        encountered_aliases.add(name)  # Add the alias to the set
        if is_deprecated:
            deprecated_license_ids[name] = license_id
    return aliases


def build_canonical_dictionary(canonical_to_file, output_dir):
    existing_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    for existing_file in existing_files:
        existing_path = os.path.join(output_dir, existing_file)
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
    process_json(spdx_license_file, is_exception=False)
    delete_file(spdx_license_file)

    download_spdx_license_list(spdx_exception_url, spdx_exception_file)
    process_json(spdx_exception_file, is_exception=True)
    delete_file(spdx_exception_file)


if __name__ == "__main__":
    main()
