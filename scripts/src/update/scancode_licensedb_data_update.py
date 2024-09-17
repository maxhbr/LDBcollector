import json
import os
import sys
import tempfile
import requests

from src.logger import setup_logger

logger = setup_logger(__name__, log_level=10)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

sys.path.append(os.path.abspath(os.path.join(script_dir, '../../')))

DATASOURCE_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def download_index_json(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        logger.debug("ScanCode index list downloaded successfully.")
    else:
        logger.debug("Failed to download ScanCode index list.")


def load_json_file(filepath):
    logger.debug("Load json file from {}".format(filepath))
    with open(filepath, 'r') as f:
        spdx_data = json.load(f)
    return spdx_data


def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.debug(f"File '{filepath}' deleted successfully.")
    else:
        logger.debug(f"File '{filepath}' does not exist.")


def download_license_json(license_key, output_file):
    url = "https://scancode-licensedb.aboutcode.org/" + license_key + ".json"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        logger.debug(f"License {license_key}.json downloaded successfully.")
    else:
        logger.debug(f"Failed to download License {license_key}.json")


def get_alias(license_data, is_spdx=True):
    license_key = None
    if is_spdx:
        license_key = license_data["key"]
    short_name = license_data["short_name"]
    name = license_data["name"]

    if "other_spdx_license_keys" in license_data:
        other_spdx_license_keys = license_data["other_spdx_license_keys"]
        alias = set(other_spdx_license_keys)

        if is_spdx:
            alias.update([license_key, short_name, name])
        else:
            alias.update([short_name, name])
    else:
        logger.debug(f"No other spdx license keys for {license_key}")
        if is_spdx:
            alias = {license_key, short_name, name}
        else:
            alias = {short_name, name}

    return list(alias)


def update_data(canonical_id, scancode_aliases):
    logger.debug(f"Updating alias for canonical id {canonical_id}")
    scancode_aliases = set(scancode_aliases)
    filepath = os.path.join(DATASOURCE_DIR, f"{canonical_id}.json")
    with open(filepath, 'r') as f:
        data = json.load(f)
        aliases = data["aliases"]
    # Prevent overwriting existing ScanCode LicenseDB entries
    if "scancode-licensedb" not in aliases:
        aliases["scancode-licensedb"] = list()
    for alias in scancode_aliases:
        if alias in data["canonical"]:
            continue
        if "spdx" in aliases:
            if alias not in aliases["spdx"] and alias not in aliases["scancode-licensedb"]:
                aliases["scancode-licensedb"].append(alias)
        else:
            if alias not in aliases["scancode-licensedb"]:
                aliases["scancode-licensedb"].append(alias)

    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def add_data(license_key, aliases):
    logger.debug(f"Adding data for {license_key}")
    output_data = {
        "canonical": license_key,
        "aliases": {
            "scancode-licensedb": aliases,
            "custom": []
        },
        "src": "scancode-licensedb"
    }

    new_output_file = os.path.join(DATASOURCE_DIR, f"{license_key}.json")

    # Write new data to the file if it does not exist or has different content
    with open(new_output_file, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)


def process_licenses():
    filepath = "licensedb_index.json"

    # Download and load index.json of ScanCode LicenseDB
    download_index_json("https://scancode-licensedb.aboutcode.org/index.json", filepath)
    index_data = load_json_file(filepath)

    exceptions = ["brian-gladman-3-clause", "bsd-2-clause-freebsd", "bsd-2-clause-netbsd", "bsl-1.0", "hidapi", "intel",
                  "libtool-exception",
                  "nokia-qt-exception-1.1", "opl-1.0", "tpl-1.0", "ubuntu-font-1.0", "ms-limited-public", "ntpl",
                  "w3c-software-20021231", "trademark-notice", "historical-sell-variant", "cmu-template",
                  "bsd-2-clause-views", "bsd-simplified", "gfdl-1.1", "gfdl-1.2", "gfdl-1.3", "x11", "openssl"]

    for lic in index_data:
        license_key = lic["license_key"]

        if license_key in exceptions:
            logger.debug(f"Skipping {license_key}")
            continue

        # Retrieve each license
        temp_dir = tempfile.TemporaryDirectory()
        filename = license_key + ".json"
        license_filepath = os.path.join(temp_dir.name, filename)
        download_license_json(license_key, license_filepath)

        license_data = load_json_file(license_filepath)
        if "spdx_license_key" in license_data:
            spdx_id = license_data["spdx_license_key"]

            if not spdx_id.startswith("LicenseRef"):
                alias = get_alias(license_data, is_spdx=True)
                update_data(spdx_id, alias)
            else:
                logger.debug("Starts with 'LicenseRef' as SPDX key")
                alias = get_alias(license_data, is_spdx=False)
                handle_data(alias, license_key)
        else:
            logger.debug(f"No SPDX license key found for {license_key}")
            alias = get_alias(license_data, is_spdx=False)
            handle_data(alias, license_key)

        temp_dir.cleanup()
    delete_file(filepath)


def handle_data(alias, license_key):
    if os.path.exists(os.path.join(DATASOURCE_DIR, f"{license_key}.json")):
        update_data(license_key, alias)
    else:
        add_data(license_key, alias)


if __name__ == "__main__":
    process_licenses()
