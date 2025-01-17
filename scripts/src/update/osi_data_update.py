import itertools
import json
import os
import sys
import requests
from src.logger import setup_logger

logger = setup_logger(__name__, log_level=10)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

sys.path.append(os.path.abspath(os.path.join(script_dir, '../../')))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def download_license_list_json(url, output_file):
    """
    Download the license list
    Args:
        url: URL to the license list
        output_file: Path to the output file
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        logger.debug("OSI license list downloaded successfully.")
    else:
        logger.debug("Failed to download OSI license list.")


def load_json_file(filepath):
    """
    Load the license list from json file and return it as a dictionary
    Args:
        filepath: Path to the license list file

    Returns:
        data (dict): Dictionary of the license list
    """
    logger.debug("Load json file from {}".format(filepath))
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def delete_file(filepath):
    """
    Delete the license list file
    Args:
        filepath: Path to the license list file
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.debug(f"File '{filepath}' deleted successfully.")
    else:
        logger.debug(f"File '{filepath}' does not exist.")


def update_data(canonical_id, osi_aliases):
    """
    Update the existing license with OSI metadata
    Args:
        canonical_id: Canonical ID for the license
        osi_aliases: List of name variation for the license
    """
    filepath = os.path.join(DATA_DIR, f"{canonical_id}.json")
    with open(filepath, 'r') as f:
        data = json.load(f)
        aliases = data.get("aliases", {})

        # Get all aliases and canonical id and flat 2D list to 1D list
        existing_aliases = list(itertools.chain.from_iterable(list(aliases.values())))
        existing_aliases.append(data.get("canonical"))

    # Add each unique alias to license if alias is not None
    for alias in osi_aliases:
        if alias not in existing_aliases and alias:
            logger.debug(f"Updating alias for canonical id {canonical_id}")

            # Create list for osi if not already existing
            if "osi" not in osi_aliases:
                aliases["osi"] = list()
            aliases["osi"].append(alias)

    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def get_aliases(entry):
    """
    Get aliases for a license entry
    Args:
        entry: The license entry from the license list

    Returns:
        aliases (list): list of aliases for the license
    """
    aliases = []

    if entry["name"]:
        aliases.append(entry["name"])
    if entry["other_names"]:
        for other_name in entry["other_names"]:
            aliases.append(other_name["name"])

    return aliases


def extract_url_id(entry):
    """
    Extract the url id from OSI Page link of a license entry
    Args:
        entry: The license entry from the license list

    Returns:
        url_id (string): the url id of the license entry

    """
    url_id = ""
    links = entry["links"]
    for link in links:
        if link["note"] == "OSI Page":
            url_id = link["url"].rsplit('/', 1)[1]
    return url_id


def process_unrecognized_license_id(aliases, license_id, url_id):
    """
    Process unrecognized license to either find the license file with all the  license name variations or return the
    unprocessed license if no match is found

    Args:
        aliases: A list of aliases associated with this license
        license_id: id of the license
        url_id: id of the url page of the license

    Returns:
        unprocessed_license_id (string): id of the unprocessed license or None if the license was found
    """

    # Get all variations of license and merge them into a list
    license_name_variations = []
    license_name_variations.extend(aliases)
    license_name_variations.extend({url_id, license_id})

    filename = get_file_for_unrecognised_id(license_name_variations)

    unprocessed_license = None
    if not filename:
        logger.warning(f"File not found for {license_id}. "
                       f"Please verify manually the existence of the license file and "
                       f"either add the new OSI license information or create a new license file in {DATA_DIR}")
        unprocessed_license = license_id
    else:
        license_id = filename.rsplit(".", 1)[0]

        update_data(license_id, license_name_variations)

    return unprocessed_license


def get_file_for_unrecognised_id(license_name_variations):
    """
    Get file path for unrecognized license id by iterating through every file and searching for matching license
    name variation.
    Args:
        license_name_variations:

    Returns:
        filename (string): file name for recognized license id or None if file isn't found
    """

    file = None
    for license_variation in license_name_variations:
        for filename in os.listdir(DATA_DIR):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                aliases = data.get("aliases", {})

                aliases = list(itertools.chain.from_iterable(list(aliases.values())))

                if license_variation in aliases:
                    file = filename
                    break
    return file


def process_licenses():
    """
    Processes the license list and updates the license entries
    """
    filepath = "osi_license_list.json"

    # Download and load index.json of OSI license list
    download_license_list_json("https://api.opensource.org/licenses/", filepath)
    license_list = load_json_file(filepath)

    files_list = os.listdir(DATA_DIR)
    unprocessed_licenses = []
    for entry in license_list:
        # Get license id and extract from the url of the OSI Page
        license_id = entry["id"]

        url_id = extract_url_id(entry)

        aliases = get_aliases(entry)

        # Process licenses where both ids are unrecognized in an extra step
        if not (f"{license_id}.json" in files_list or f"{url_id}.json" in files_list):
            unprocessed_license = process_unrecognized_license_id(aliases, license_id, url_id)
            if unprocessed_license:
                unprocessed_licenses.append(unprocessed_license)
        else:
            if f"{license_id}.json" in files_list:
                aliases.append(url_id)
                update_data(license_id, aliases)
            else:
                aliases.append(license_id)
                update_data(url_id, aliases)
    if unprocessed_licenses:
        logger.info(f"Unprocessed {len(unprocessed_licenses)}\n"
                    f"{unprocessed_licenses}")
    delete_file(filepath)


if __name__ == "__main__":
    process_licenses()
