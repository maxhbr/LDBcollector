#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import logging
import os

from src.update.BaseDataUpdate import BaseDataUpdate


class SpdxDataUpdate(BaseDataUpdate):
    def __init__(self, debug=False):
        super().__init__(src="spdx", log_level=logging.DEBUG)
        if debug:
            super().__init__(src="spdx", log_level=logging.DEBUG)
        else:
            super().__init__(src="spdx", log_level=logging.INFO)

    def update_non_spdx_license_file(self, license_id: str, data: dict, old_license_filepath: str, license_name: str) -> None:
        """
        Update the license file where the source is not SPDX to SPDX by adding SPDX data to the license file and rename
        the license file to the new canonical id
        Args:
            license_id: id of the spdx license
            data: data to update
            old_license_filepath: filepath to already existing license file
            license_name: name of the SPDX license for aliases
        """
        self._LOGGER.info(f"Updating non spdx license source with spdx source for {license_id}...")

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

        data["src"] = self._src
        data["canonical"] = license_id
        if old_canonical_id is not license_id:
            data["aliases"][old_src].append(old_canonical_id)

        new_license_filepath = os.path.join(self._DATA_DIR, f"{license_id}.json")

        os.rename(old_license_filepath, new_license_filepath)

        with open(new_license_filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def process_unrecognized_license_id(self, aliases: list, license_id: str) -> str | None:
        """
        Process unrecognized license to either find the license file with all the  license name variations or return the
        unprocessed license if no match is found

        Args:
            aliases: A list of aliases associated with this license
            license_id: id of the license

        Returns:
            license_id (string): the id of the license if the license file is not found or None
        """
        self._LOGGER.debug(f"Processing unrecognized license {license_id}...")

        # Get all variations of license and merge them into a list
        license_name_variations = []
        license_name_variations.extend(aliases)
        license_name_variations.extend([license_id])

        filename = self.get_file_for_unrecognized_id(license_name_variations)

        if not filename:
            self._LOGGER.info(f"File not found for {license_id}.\n"
                              f"Please edit license file manually if the license already exists or"
                              f" create a new license file.")
            return license_id
        else:
            license_file_id = filename.rsplit(".", maxsplit=1)[0]
            license_filepath = os.path.join(self._DATA_DIR, f"{license_file_id}.json")
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

        files_list = os.listdir(self._DATA_DIR)

        for entry in license_list:
            # Get license id and extract from the url of the SPDX Page
            license_id = entry[json_id]

            # Process licenses where both ids are unrecognized in an extra step
            if f"{license_id}.json" not in files_list:
                unprocessed_license_id = self.process_unrecognized_license_id([entry["name"]], license_id)
                if unprocessed_license_id:
                    self.create_license_file(unprocessed_license_id, [entry["name"]])
            else:
                license_filepath = os.path.join(self._DATA_DIR, f"{license_id}.json")
                data = self.load_json_file(license_filepath)
                if data["src"] == "spdx":
                    self.update_license_file(license_id, [entry["name"]])
                else:
                    self.update_non_spdx_license_file(license_id, data, license_filepath, entry["name"])

        self.delete_file(filepath)

    def process_licenses(self):
        """
        Processes the SPDX license and exception list and summarizes the unprocessed licenses.
        """
        spdx_licenses_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"

        spdx_exceptions_url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json"

        self._process_licenses(spdx_licenses_url, "licenseId", "licenses")

        self._process_licenses(spdx_exceptions_url, "licenseExceptionId", "exceptions")
