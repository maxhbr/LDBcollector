#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import itertools
import json
import os
import re
import sys
import requests

from src.logger import setup_logger


class BaseDataUpdate:
    def __init__(self, src: str, log_level=10):
        self._LOGGER = setup_logger(__name__, log_level=log_level)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        sys.path.append(os.path.abspath(os.path.join(script_dir, '../../')))

        self._DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))

        self._src = src

    def download_json_file(self, url: str, output_filepath) -> None:
        """
            Download the license list
            Args:
                url: URL to the license list
                output_filepath: Path to the output file
            """
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_filepath, 'wb') as f:
                f.write(response.content)
            self._LOGGER.debug(f"{self._src} license list downloaded successfully.")
        else:
            self._LOGGER.debug(f"Failed to download {self._src} license list.")

    def load_json_file(self, filepath: str) -> dict:
        """
        Load the license list from json file and return it as a dictionary
        Args:
            filepath: Path to the license list file

        Returns:
            data (dict): Dictionary of the license list
        """
        self._LOGGER.debug("Load json file from {}".format(filepath))
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data

    def delete_file(self, filepath) -> None:
        """
        Delete the license list file
        Args:
            filepath: Path to the license list file
        """
        if os.path.exists(filepath):
            os.remove(filepath)
            self._LOGGER.debug(f"File '{filepath}' deleted successfully.")
        else:
            self._LOGGER.debug(f"File '{filepath}' does not exist.")

    def update_license_file(self, canonical_id: str, aliases: list[str]) -> None:
        """
        Update the existing license with metadata
        Args:
            canonical_id: Canonical ID for the license
            aliases: List of name variations for the license
        """
        filepath = os.path.join(self._DATA_DIR, f"{canonical_id}.json")

        data = self.load_json_file(filepath)
        existing_aliases = data.get("aliases", {})

        risky_aliases = data.get("risky", [])
        rejected_aliases = data.get("rejected", [])

        # Get all aliases and canonical id and flat 2D list to 1D list and add canonical ID to prevent duplication
        aliases_list = list(itertools.chain.from_iterable(list(existing_aliases.values())))
        aliases_list.append(data["canonical"]["id"])

        normalized_aliases = self._normalize_alias_list(aliases)

        # Add each unique alias to license if alias is not None
        for alias in normalized_aliases:
            if alias in risky_aliases:
                self._LOGGER.debug(f"For {canonical_id} the alias '{alias}' is already in risky list")
                continue
            if alias in rejected_aliases:
                self._LOGGER.debug(f"For {canonical_id} the alias '{alias}' is already in rejected list")
                continue
            if alias not in aliases_list:
                self._LOGGER.debug(f"Updating alias for canonical id {canonical_id}")

                # Create list for the source if not already existing
                if self._src not in data["aliases"]:
                    existing_aliases[self._src] = list()
                existing_aliases[self._src].append(alias)

        custom_aliases = self._create_custom_list_for_quotes(normalized_aliases)

        for alias in custom_aliases:
            if alias not in aliases_list:
                existing_aliases["custom"].append(alias)

        with open(filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def create_license_file(self, canonical_id: str, aliases: list[str]) -> None:
        """
        Creates the license file for the given license ID and name
        Args:
            canonical_id: Unique identifier for the license
            aliases: Dictionary of aliases of the license
        """
        self._LOGGER.debug(f"Creating new data file: {canonical_id}.json")

        normalized_aliases = self._normalize_alias_list(aliases)

        custom_list = self._create_custom_list_for_quotes(normalized_aliases)

        output_data = {
            "canonical": {
                "id": canonical_id,
                "src": self._src,
            },
            "aliases": {
                self._src: normalized_aliases,
                "custom": custom_list
            },
            "rejected": [],
            "risky": []
        }

        filepath = os.path.join(self._DATA_DIR, f"{canonical_id}.json")
        # Write new data to the file
        with open(filepath, 'w') as outfile:
            json.dump(output_data, outfile, indent=4)

    def get_file_for_unrecognized_id(self, license_name_variations: list[str]) -> str | None:
        """
        Get file path for unrecognized license id by iterating through every file and searching for matching license
        name variation.
        Args:
            license_name_variations: list of license name variations to find the license file

        Returns:
            filename (string): file name for recognized license id or None if file isn't found
        """
        self._LOGGER.debug(f"Searching for unrecognized license id for {license_name_variations}...")

        file = None
        for license_variation in license_name_variations:
            for filename in os.listdir(self._DATA_DIR):
                filepath = os.path.join(self._DATA_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    aliases = data.get("aliases", {})

                    aliases = list(itertools.chain.from_iterable(list(aliases.values())))

                    if license_variation in aliases:
                        self._LOGGER.debug(f"Found with {license_variation} in file {filename}")
                        file = filename
                        break
        return file

    def _normalize_quotes(self, input_string: str, replacement: str = "'") -> str:
        """
        Normalize a string by replacing various Unicode and ASCII quote characters
        with a single default quote character. By default, all quotes (both single and double)
        are mapped to the ASCII single quote.

        Args:
            input_string (str): The input text that potentially contains various quote characters.
            replacement (str, optional): The quote character replacement to use. Defaults to "'".

        Returns:
            str: The normalized text with all recognized quote characters replaced.
        """
        self._LOGGER.debug(f"Normalizing quotes: {input_string}")
        # List of quote characters to replace with the default replacement.
        quote_characters = [
            # Single quotes
            "\u2018",  # LEFT SINGLE QUOTATION MARK ‘
            "\u2019",  # RIGHT SINGLE QUOTATION MARK ’
            "\u201A",  # SINGLE LOW-9 QUOTATION MARK ‚
            "\u201B",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK ‛
            "\u2032",  # PRIME (often used as an apostrophe) ′
            "\uFF07",  # FULLWIDTH APOSTROPHE ＇
            # Double quotes
            "\u201C",  # LEFT DOUBLE QUOTATION MARK “
            "\u201D",  # RIGHT DOUBLE QUOTATION MARK ”
            "\u201E",  # DOUBLE LOW-9 QUOTATION MARK „
            "\u201F",  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK ‟
            "\u2033",  # DOUBLE PRIME ″
            "\u00AB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK «
            "\u00BB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK »
            "\uFF02",  # FULLWIDTH QUOTATION MARK ＂
        ]

        # Create a translation mapping from the Unicode code point of each quote character
        # to the desired replacement.
        translation_map = {ord(char): replacement for char in quote_characters}
        normalized_input_string = input_string.translate(translation_map)
        return normalized_input_string

    def _normalize_alias_list(self, aliases: list[str]) -> list[str]:
        """
        Normalize the alias list by replacing various Unicode and ASCII quote characters with a single default quote character.

        Args:
            aliases (list[str]): The alias list to normalize

        Returns:
            list[str]: The normalized alias list
        """
        normalized_aliases = list()

        for alias in aliases:
            normalized_alias = self._normalize_quotes(alias)
            normalized_aliases.append(normalized_alias)
        normalized_aliases.sort()
        return normalized_aliases

    def _create_custom_list_for_quotes(self, aliases: list[str]) -> list[str]:
        """
        Create custom list for quote characters by calling for each alias in the aliases list the method
        _create_custom_entry_for_quotes and returning the custom list.

        Args:
            aliases (list[str]): The alias list to create custom list for quote characters

        Returns:
            list[str]: The created custom list
        """
        custom_aliases: list[str] = list()
        for alias in aliases:
            self._create_custom_entry_for_quotes(alias, custom_aliases)
        custom_aliases.sort()
        return custom_aliases

    def _create_custom_entry_for_quotes(self, alias: str, aliases: list[str]) -> None:
        """
        Create custom entry for an alias with words or phrases surrounded by quotes. When the word or phrase has single
        quote characters, it will be replaced with a double quote characters and vice versa.

        Args:
            alias (str): The alias to create custom entry for
``          aliases (dict[str, list[str]]): The alias dictionary to put the custom entry in
        """
        pattern = re.compile(r'(?<!\w)(["\'])(.+?)\1(?!\w)')

        if pattern.search(alias):
            new_alias = pattern.sub(self._swap_quotes, alias)
            if new_alias not in aliases:
                aliases.append(new_alias)

    @staticmethod
    def _swap_quotes(match):
        quote, text = match.groups()
        return f'"{text}"' if quote == "'" else f"'{text}'"
