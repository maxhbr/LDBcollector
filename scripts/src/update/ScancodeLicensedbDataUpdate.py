#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import logging
import os
from dotenv import load_dotenv
from src.update.BaseDataUpdate import BaseDataUpdate


class ScancodeLicensedbDataUpdate(BaseDataUpdate):
    def __init__(self, debug=False):
        if debug:
            super().__init__(src="scancode-licensedb", log_level=logging.DEBUG)
        else:
            super().__init__(src="scancode-licensedb", log_level=logging.INFO)

        self._base_url = "https://scancode-licensedb.aboutcode.org/"
        self._index_url = f"{self._base_url}index.json"

        load_dotenv()

        self._EXCEPTION_SCANCODE_LICENSEDB = os.getenv('EXCEPTION_SCANCODE_LICENSEDB')

    def get_aliases(self, license_data: dict, is_spdx=True) -> list[str]:
        """
        Get the aliases for the given license
        Args:
            license_data: license data from the individual license
            is_spdx: whether to append the "key" to the list of aliases

        Returns:
            aliases (list): the aliases for the given license
        """
        short_name = license_data["short_name"]
        name = license_data["name"]
        aliases = {short_name, name}

        if is_spdx:
            license_key = license_data["key"]
            aliases.update([license_key])
        if "spdx_license_key" in license_data and license_data["spdx_license_key"].startswith("LicenseRef"):
            license_ref_spdy_key = license_data["spdx_license_key"]
            aliases.update([license_ref_spdy_key])
        if "other_spdx_license_keys" in license_data:
            other_spdx_license_keys = license_data["other_spdx_license_keys"]
            aliases.update(other_spdx_license_keys)

        return list(aliases)

    def process_unrecognized_license_id(self, aliases: list[str], license_id: str) -> str | None:
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
            self._LOGGER.info(f"File not found for {license_id}.\n")
            return license_id
        return None

    def handle_data(self, aliases: list[str], license_key: str) -> None:
        """
        Determine if a license file must be updated or created
        Args:
            aliases: List of license name variations
            license_key: ScanCode LicenseDB's license key
        """

        if os.path.exists(os.path.join(self._DATA_DIR, f"{license_key}.json")):
            self.update_license_file(license_key, aliases)
        else:
            unrecognized_license_id = self.process_unrecognized_license_id(aliases, license_key)
            if unrecognized_license_id:
                self.create_license_file(unrecognized_license_id, aliases)

    def process_licenses(self) -> None:
        """
        Process licenses for scancode-licensedb
        """

        filepath = "licensedb_index.json"

        # Download and load index.json of ScanCode LicenseDB
        self.download_json_file(self._index_url, filepath)
        index_data = self.load_json_file(filepath)

        for lic in index_data:
            license_key = lic["license_key"]

            if license_key in self._EXCEPTION_SCANCODE_LICENSEDB:
                self._LOGGER.debug(f"Skipping {license_key}")
                continue

            # Create filepath
            filename = license_key + ".json"
            license_filepath = os.path.join(filename)

            # Download license to specified filepath and load downloaded json file as dictionary
            url = self._base_url + license_key + ".json"
            self.download_json_file(url, license_filepath)

            license_data = self.load_json_file(license_filepath)

            if "spdx_license_key" in license_data:
                spdx_id = license_data["spdx_license_key"]

                if not spdx_id.startswith("LicenseRef"):
                    self._LOGGER.debug(f"{license_key} is already a spdx license")
                    aliases = self.get_aliases(license_data, is_spdx=True)
                    self.update_license_file(spdx_id, aliases)
                else:
                    self._LOGGER.debug("Starts with 'LicenseRef' as SPDX key")
                    aliases = self.get_aliases(license_data, is_spdx=False)
                    self.handle_data(aliases, license_key)
            else:
                self._LOGGER.debug(f"No SPDX license key found for {license_key}")
                aliases = self.get_aliases(license_data, is_spdx=False)
                self.handle_data(aliases, license_key)

            self.delete_file(license_filepath)
        self.delete_file(filepath)
