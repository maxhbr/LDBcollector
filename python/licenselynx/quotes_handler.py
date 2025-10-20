#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: BSD-3-Clause
#
class _QuotesHandler:
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

    def normalize_quotes(self, input_string: str, replacement: str = "'") -> str:
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
        translation_map = {ord(char): replacement for char in self.quote_characters}
        normalized_input_string = input_string.translate(translation_map)
        return normalized_input_string
