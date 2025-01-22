import itertools
import json
import logging
import os

from src.update.BaseDataUpdate import BaseDataUpdate


class SpdxDataUpdate(BaseDataUpdate):
    def __init__(self):
        super().__init__(src="spdx", log_level=logging.DEBUG)

    def update_non_spdx_license_file(self, license_id, data, old_license_filepath, license_name):
        """
        Update the license file where the source is not SPDX to SPDX by adding SPDX data to the license file and rename
        the license file to the new canonical id
        Args:
            license_id: id of the spdx license
            data: data to update
            old_license_filepath: filepath to already existing license file
            license_name: name of the SPDX license for aliases
        """
        self.LOGGER.info(f"Updating non spdx license source with spdx source for {license_id}...")

        # Remove SPDX id and name variation if it is already saved in another source
        for alias in data["aliases"].items():
            if license_id in alias[1]:
                data["aliases"][alias[0]].remove(license_id)
            if license_name in alias[1] and alias[0] != "spdx":
                data["aliases"][alias[0]].remove(license_name)

        # If spdx entry to aliases if it does not exist
        if "spdx" not in data["aliases"]:
            data["aliases"].update({"spdx": [license_name]})

        # Update old canonical name and source with new SPDX data
        old_src = data["src"]
        old_canonical_id = data["canonical"]

        data["src"] = self.src
        data["canonical"] = license_id
        if old_canonical_id is not license_id:
            data["aliases"][old_src].append(old_canonical_id)

        new_license_filepath = os.path.join(self.DATA_DIR, f"{license_id}.json")

        os.rename(old_license_filepath, new_license_filepath)

        with open(new_license_filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

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

    def process_unrecognized_license_id(self, aliases, license_id):
        """
        Process unrecognized license to either find the license file with all the  license name variations or return the
        unprocessed license if no match is found

        Args:
            aliases: A list of aliases associated with this license
            license_id: id of the license

        Returns:
            license_id (string): the id of the license if the license file is not found or None
        """
        self.LOGGER.debug(f"Processing unrecognized license {license_id}...")

        # Get all variations of license and merge them into a list
        license_name_variations = []
        license_name_variations.extend(aliases)
        license_name_variations.extend([license_id])

        filename = self.get_file_for_unrecognised_id(license_name_variations)

        if not filename:
            self.LOGGER.info(f"File not found for {license_id}.\n"
                             f"Please edit license file manually if the license already exists or"
                             f" create a new license file.")
            return license_id
        else:
            license_file_id = filename.rsplit(".", maxsplit=1)[0]
            license_filepath = os.path.join(self.DATA_DIR, f"{license_file_id}.json")
            data = self.load_json_file(license_filepath)

            if data["src"] == "spdx":
                self.update_license_file(license_file_id, license_name_variations)
            else:
                self.update_non_spdx_license_file(license_id, data, license_filepath, aliases[0])
            return None

    def _process_licenses(self, url: str, json_id: str, license_list_type: str):
        """
        Processes the SPDX license list with the given url, json ID and license list type and either update or create
        a license file
        Args:
            url: URL of the SPDX license list
            json_id: SPDX license id
            license_list_type: Either "license" or "exception"
        """
        filepath = "spdx_license_list.json"

        # Download and load index.json of SPDX license list
        self.download_json_file(url, filepath)
        license_list = self.load_json_file(filepath)[license_list_type]

        files_list = os.listdir(self.DATA_DIR)

        unprocessed_licenses = []

        for entry in license_list:
            # Get license id and extract from the url of the SPDX Page
            license_id = entry[json_id]

            # Process licenses where both ids are unrecognized in an extra step
            if f"{license_id}.json" not in files_list:
                unprocessed_license_id = self.process_unrecognized_license_id([entry["name"]], license_id)
                if unprocessed_license_id:
                    unprocessed_licenses.append(unprocessed_license_id)
            else:
                license_filepath = os.path.join(self.DATA_DIR, f"{license_id}.json")
                data = self.load_json_file(license_filepath)
                if data["src"] == "spdx":
                    self.update_license_file(license_id, [entry["name"]])
                else:
                    self.update_non_spdx_license_file(license_id, data, license_filepath, entry["name"])

        self.delete_file(filepath)

        return unprocessed_licenses

    def process_licenses(self):
        """
        Processes the SPDX license and exception list and summarizes the unprocessed licenses.
        """
        spdx_licenses_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"

        spdx_exceptions_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json"

        unprocessed_licenses = {}

        unprocessed_licenses.update(
            {"licenses": self._process_licenses(spdx_licenses_url, "licenseId", "licenses")})
        unprocessed_licenses.update(
            {"exceptions": self._process_licenses(spdx_exceptions_url, "licenseExceptionId", "exceptions")})

        number_unprocessed_licenses = len(unprocessed_licenses["licenses"]) + len(unprocessed_licenses["exceptions"])
        self.LOGGER.info(f"Processed {number_unprocessed_licenses}.\n"
                         f"{unprocessed_licenses}")
