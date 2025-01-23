import itertools
import json
import os
import sys
import requests

from src.logger import setup_logger


class BaseDataUpdate:
    def __init__(self, src: str, log_level=10):
        self.LOGGER = setup_logger(__name__, log_level=log_level)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        sys.path.append(os.path.abspath(os.path.join(script_dir, '../../')))

        self.DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))

        self.src = src

    def download_json_file(self, url, output_file):
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
            self.LOGGER.debug(f"{self.src} license list downloaded successfully.")
        else:
            self.LOGGER.debug(f"Failed to download {self.src} license list.")

    def load_json_file(self, filepath):
        """
        Load the license list from json file and return it as a dictionary
        Args:
            filepath: Path to the license list file

        Returns:
            data (dict): Dictionary of the license list
        """
        self.LOGGER.debug("Load json file from {}".format(filepath))
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data

    def delete_file(self, filepath):
        """
        Delete the license list file
        Args:
            filepath: Path to the license list file
        """
        if os.path.exists(filepath):
            os.remove(filepath)
            self.LOGGER.debug(f"File '{filepath}' deleted successfully.")
        else:
            self.LOGGER.debug(f"File '{filepath}' does not exist.")

    def update_license_file(self, canonical_id: str, aliases: list):
        """
        Update the existing license with metadata
        Args:
            canonical_id: Canonical ID for the license
            aliases: List of name variations for the license
        """
        filepath = os.path.join(self.DATA_DIR, f"{canonical_id}.json")

        data = self.load_json_file(filepath)
        existing_aliases = data.get("aliases", {})

        # Get all aliases and canonical id and flat 2D list to 1D list and add canonical ID to prevent duplication
        aliases_list = list(itertools.chain.from_iterable(list(existing_aliases.values())))
        aliases_list.append(data.get("canonical"))

        # Add each unique alias to license if alias is not None
        for alias in aliases:
            if alias not in aliases_list:
                self.LOGGER.debug(f"Updating alias for canonical id {canonical_id}")

                # Create list for the source if not already existing
                if self.src not in data["aliases"]:
                    existing_aliases[self.src] = list()
                existing_aliases[self.src].append(alias)

        with open(filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def create_license_file(self, canonical_id, aliases):
        """
        Creates the license file for the given license ID and name
        Args:
            canonical_id: Unique identifier for the license
            aliases: Dictionary of aliases of the license
        """
        self.LOGGER.debug(f"Creating new data file: {canonical_id}.json")
        # Determine the aliases for the current license
        output_data = {
            "canonical": canonical_id,
            "aliases": {
                self.src: aliases,
                "custom": []
            },
            "src": self.src
        }

        filepath = os.path.join(self.DATA_DIR, f"{canonical_id}.json")
        # Write new data to the file
        with open(filepath, 'w') as outfile:
            json.dump(output_data, outfile, indent=4)

    def get_file_for_unrecognised_id(self, license_name_variations):
        """
        Get file path for unrecognized license id by iterating through every file and searching for matching license
        name variation.
        Args:
            license_name_variations:

        Returns:
            filename (string): file name for recognized license id or None if file isn't found
        """
        self.LOGGER.debug(f"Searching for unrecognized license id for {license_name_variations}...")

        file = None
        for license_variation in license_name_variations:
            for filename in os.listdir(self.DATA_DIR):
                filepath = os.path.join(self.DATA_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    aliases = data.get("aliases", {})

                    aliases = list(itertools.chain.from_iterable(list(aliases.values())))

                    if license_variation in aliases:
                        self.LOGGER.debug(f"Found with {license_variation} in file {filename}")
                        file = filename
                        break
        return file
