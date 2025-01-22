import os
from dotenv import load_dotenv
from src.update.BaseDataUpdate import BaseDataUpdate


class ScancodeLicensedbDataUpdate(BaseDataUpdate):
    def __init__(self):
        super().__init__(src="scancode-licensedb")

        load_dotenv()

        self.EXCEPTION_SCANCODE_LICENSEDB = os.getenv('EXCEPTION_SCANCODE_LICENSEDB')

    def get_aliases(self, license_data, is_spdx=True):
        """
        Get the aliases for the given license
        Args:
            license_data: license data from the individual license
            is_spdx: whether to append the "key" to the list of aliases

        Returns:
            aliases (list): the aliases for the given license
        """

        license_key = None
        if is_spdx:
            license_key = license_data["key"]
        short_name = license_data["short_name"]
        name = license_data["name"]

        license_ref_spdy_key = None

        if "spdx_license_key" in license_data and license_data["spdx_license_key"].startswith("LicenseRef"):
            license_ref_spdy_key = license_data["spdx_license_key"]
        if "other_spdx_license_keys" in license_data:
            other_spdx_license_keys = license_data["other_spdx_license_keys"]
            aliases = set(other_spdx_license_keys)

            if is_spdx:
                aliases.update([license_key, short_name, name])
            else:
                aliases.update([short_name, name])
            if license_ref_spdy_key:
                aliases.update([license_ref_spdy_key])
        else:
            self.LOGGER.debug(f"No other spdx license keys for {license_data['key']}")
            if is_spdx:
                aliases = {license_key, short_name, name}
            else:
                aliases = {short_name, name}

            if license_ref_spdy_key:
                aliases.update([license_ref_spdy_key])

        return list(aliases)

    def handle_data(self, aliases, license_key):
        """
        Determine if a license file must be updated or created
        Args:
            aliases: List of license name variations
            license_key: ScanCode LicenseDB's license key
        """

        if os.path.exists(os.path.join(self.DATA_DIR, f"{license_key}.json")):
            self.update_license_file(license_key, aliases)
        else:
            output_filepath = os.path.join(self.DATA_DIR, f"{license_key}.json")
            self.create_license_file(license_key, aliases, output_filepath)

    def process_licenses(self):
        """
        Process licenses for scancode-licensedb
        """

        filepath = "licensedb_index.json"

        # Download and load index.json of ScanCode LicenseDB
        self.download_json_file("https://scancode-licensedb.aboutcode.org/index.json", filepath)
        index_data = self.load_json_file(filepath)

        for lic in index_data:
            license_key = lic["license_key"]

            if license_key in self.EXCEPTION_SCANCODE_LICENSEDB:
                self.LOGGER.debug(f"Skipping {license_key}")
                continue

            # Create filepath
            filename = license_key + ".json"
            license_filepath = os.path.join(filename)

            # Download license to specified filepath and load downloaded json file as dictionary
            url = "https://scancode-licensedb.aboutcode.org/" + license_key + ".json"
            self.download_json_file(url, license_filepath)

            license_data = self.load_json_file(license_filepath)

            if "spdx_license_key" in license_data:
                spdx_id = license_data["spdx_license_key"]

                if not spdx_id.startswith("LicenseRef"):
                    self.LOGGER.debug(f"{license_key} is already a spdx license")
                    aliases = self.get_aliases(license_data, is_spdx=True)
                    self.update_license_file(spdx_id, aliases)
                else:
                    self.LOGGER.debug("Starts with 'LicenseRef' as SPDX key")
                    aliases = self.get_aliases(license_data, is_spdx=False)
                    self.handle_data(aliases, license_key)
            else:
                self.LOGGER.debug(f"No SPDX license key found for {license_key}")
                aliases = self.get_aliases(license_data, is_spdx=False)
                self.handle_data(aliases, license_key)

            self.delete_file(license_filepath)
        self.delete_file(filepath)
