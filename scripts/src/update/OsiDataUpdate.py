import os
from src.update.BaseDataUpdate import BaseDataUpdate


class OsiDataUpdate(BaseDataUpdate):
    def __init__(self):
        super().__init__(src="osi")

    @staticmethod
    def get_aliases(entry: dict) -> list[str]:
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

    @staticmethod
    def extract_url_id(entry: dict) -> str | None:
        """
        Extract the url id from OSI Page link of a license entry
        Args:
            entry: The license entry from the license list

        Returns:
            url_id (string): the url id of the license entry

        """
        url_id = None
        links = entry["links"]
        for link in links:
            if link["note"] == "OSI Page":
                url_id = link["url"].rsplit('/', 1)[1]
        return url_id

    def process_unrecognized_license_id(self, aliases: list[str], license_id: str, url_id: str) -> str | None:
        """
        Process unrecognized license to either find the license file with all the  license name variations or return the
        unprocessed license if no match is found

        Args:
            aliases: A list of aliases associated with this license
            license_id: id of the license
            url_id: id of the url page of the license

        Returns:
            unprocessed_license_id (string): id of the still unrecognized license or None if the license was found
        """

        # Get all variations of license and merge them into a list
        license_name_variations = []
        license_name_variations.extend(aliases)
        license_name_variations.extend({url_id, license_id})

        filename = self.get_file_for_unrecognized_id(license_name_variations)

        unprocessed_license = None
        if not filename:
            self._LOGGER.warning(f"File not found for {license_id}. "
                                 f"Please verify manually the existence of the license file and either add the new "
                                 f"OSI license information or create a new license file in {self._DATA_DIR}")
            unprocessed_license = license_id
        else:
            license_id = filename.rsplit(".", 1)[0]

            self.update_license_file(license_id, license_name_variations)

        return unprocessed_license

    def process_licenses(self):
        """
        Processes the license list and updates the license entries
        """
        filepath = "osi_license_list.json"

        # Download and load index.json of OSI license list
        self.download_json_file("https://api.opensource.org/licenses/", filepath)
        license_list = self.load_json_file(filepath)

        files_list = os.listdir(self._DATA_DIR)
        unprocessed_licenses = []
        for entry in license_list:
            # Get license id and extract from the url of the OSI Page
            license_id = entry["id"]

            url_id = self.extract_url_id(entry)

            aliases = self.get_aliases(entry)

            # Process licenses where both ids are unrecognized in an extra step
            if not (f"{license_id}.json" in files_list or f"{url_id}.json" in files_list):
                unprocessed_license = self.process_unrecognized_license_id(aliases, license_id, url_id)
                if unprocessed_license:
                    unprocessed_licenses.append(unprocessed_license)
            else:
                if f"{license_id}.json" in files_list:
                    aliases.append(url_id)
                    self.update_license_file(license_id, aliases)
                else:
                    aliases.append(license_id)
                    self.update_license_file(url_id, aliases)
        if unprocessed_licenses:
            self._LOGGER.info(f"Unprocessed licenses: {len(unprocessed_licenses)}\n"
                              f"{unprocessed_licenses}")
        self.delete_file(filepath)
