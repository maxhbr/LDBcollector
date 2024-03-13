# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


import json
import yaml

OUTPUT_FORMAT_JSON = 'Json'
OUTPUT_FORMAT_YAML = 'Yaml'
OUTPUT_FORMAT_TEXT = 'text'
OUTPUT_FORMATS = [OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_YAML, OUTPUT_FORMAT_TEXT]
"""Allowed formats (case insensitive): Json, Yaml, text."""

class OutputFormatterFactory():

    @staticmethod
    def formatter(_format):
        """
        Return a formatter corresponding to the supplied format

        :param format: format for the output
        :type format: str
        :return: a normalized license expression, None if invalied format
        :rtype: OutputFormatter

        :Example:

        >>> formatter = OutputFormatterFactory.formatter("JSON")
        """
        if _format.lower() == OUTPUT_FORMAT_JSON.lower():
            return JsonOutputFormatter()
        elif _format.lower() == OUTPUT_FORMAT_YAML.lower():
            return YamlOutputFormatter()
        elif _format.lower() == OUTPUT_FORMAT_TEXT.lower():
            return TextOutputFormatter()

class OutputFormatter():
    """Base class for implementing sub classes providing methods for
    formatting data as returned from the various methods in the
    FossLicense class.

    There are no constructors, please use  :func:`flame.format.OutputFormatterFactory.formatter` instead.  See OUTPUT_FORMATS
    """

    def format_compat(self, compat, verbose=False):
        """
        Return a formatted string of the compatibility as returned by :func:`flame.license_db.FossLicenses.expression_compatibility_as`

        :param compat: A compatibitility as returned by expression_compatibility_as.
        :type compat: dict
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if compat is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> from flame.format import OutputFormatterFactory
        >>> fl = FossLicenses()
        >>> compat = fl.expression_compatibility_as('x11-keith-packard')
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted, warnings = formatter.format_compatibilities(compat)
        >>> print(formatted)
        HPND
        """
        return None, None

    def format_compat_list(self, all_compats, verbose=False):
        """
        Return a formatted string of the compatibilities :func:`flame.license_db.FossLicenses.compatibility_as_list`.

        :param all_compats: A list of compatibitility as returned from compatibility_as_list
        :type all_compats: list
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if all_compats is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> compat = fl.compatibility_as_list()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_compat_list(compat)

        """
        return None, None

    def format_expression(self, expression, verbose=False):
        """
        Return a formatted string of the compatibilities :func:`flame.license_db.FossLicenses.alias_list`.

        :param all_aliases: A list of aliases as returned from FossLicenses.alias_list()
        :type all_aliases: list
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if all_compats is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> compat = fl.alias_list()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_alias_list(compat)

        """
        return None, None

    def format_alias_list(self, all_aliases, verbose=False):
        """
        Return a formatted string of the compatibilities :func:`flame.license_db.FossLicenses.alias_list`.

        :param all_aliases: A list of aliases as returned from FossLicenses.alias_list()
        :type all_aliases: list
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if all_compats is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> compat = fl.alias_list()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_alias_list(compat)

        """
        return None, None

    def format_error(self, message, verbose=False):
        """
        Return a formatted string of an error message

        :param message: Error message, typically received via an exception
        :type message: str
        :param verbose: provide additional information
        :type verbose: boolean
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.exception import FlameException
        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> try:
        ...     aliases = fl.aliases("do no exist")
        ... except FlameException as e:
        ...     formatted = formatter.format_error(e)

        """
        return None, None

    def format_licenses(self, licenses, verbose=False):
        """
        Return a formatted string of a list of licenses

        :param licenses: list of licenses
        :type message: [str]
        :param verbose: provide additional information
        :type verbose: boolean
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> licenses = fl.licenses()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_licenses(licenses)

        """
        return None, None

    def format_license_complete(self, lic, verbose=False):
        """
        Return a formatted string of a complete license listing

        :param lic: license to format
        :type message: [str]
        :param verbose: provide additional information
        :type verbose: boolean
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> licenses = fl.license_complete("MIT")
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_license_complete(licenses)

        """
        return None, None

    def format_compatibilities(self, compats, verbose=False):
        """
        Return a formatted string of the provided compatibilities.

        :param : A list of aliases as returned from FossLicenses.alias_list()
        :type all_aliases: list
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if all_compats is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> compatibilities = fl.expression_compatibility_as("MIT & GPLv2+")
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_compatibilities(compatibilities)

        """
        return None, None

    def format_operators(self, operators, verbose=False):
        """
        Return a formatted string of the provided operators

        :param operators: A list of operators.
        :type operators: list
        :param verbose: provide additional information
        :type verbose: boolean
        :raise FlameException: if all_compats is not valid
        :return: formatted string
        :rtype: str

        :Example:

        >>> from flame.license_db import FossLicenses
        >>> fl = FossLicenses()
        >>> operators = fl.operators()
        >>> formatter = OutputFormatterFactory.formatter("TEXT")
        >>> formatted = formatter.format_operators(operators)

        """
        return None, None

class JsonOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose=False):
        return json.dumps(compat, indent=4), None

    def format_compat_list(self, all_compats, verbose=False):
        return json.dumps(all_compats, indent=4), None

    def format_expression(self, expression, verbose=False):
        return json.dumps(expression, indent=4), None

    def format_alias_list(self, all_aliases, verbose=False):
        return json.dumps(all_aliases, indent=4), None

    def format_error(self, error, verbose=False):
        new_error = {
            'message': str(error),
            'problems': error.problems(),
        }
        return json.dumps(new_error, indent=4), None

    def format_licenses(self, licenses, verbose=False):
        return json.dumps(licenses, indent=4), None

    def format_license_complete(self, _license, verbose=False):
        return json.dumps(_license, indent=4), None

    def format_compatibilities(self, compats, verbose=False):
        return json.dumps(compats), None

    def format_operators(self, operators, verbose=False):
        return json.dumps(operators), None

class YamlOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose=False):
        return yaml.safe_dump(compat), None

    def format_compat_list(self, all_compats, verbose=False):
        return None, None

    def format_expression(self, expression, verbose=False):
        return yaml.safe_dump(expression), None

    def format_alias_list(self, all_aliases, verbose=False):
        return yaml.safe_dump(all_aliases), None

    def format_error(self, error, verbose=False):
        return yaml.safe_dump({'error': f'{error}'}), None

    def format_licenses(self, licenses, verbose=False):
        return yaml.safe_dump(licenses), None

    def format_license_complete(self, _license, verbose=False):
        return yaml.safe_dump(_license), None

    def format_compatibilities(self, compats, verbose=False):
        return yaml.safe_dump(compats), None

    def format_operators(self, operators, verbose=False):
        return yaml.safe_dump(operators), None

class TextOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose=False):
        ret = []
        id_lic = compat['identified_license']
        if verbose:
            ret.append(f'queried_name: {id_lic["queried_name"]}')
            ret.append(f'name: {id_lic["name"]}')
            ret.append(f'identified via: {id_lic["identified_via"]}')
            ret.append(f'compatibility:  {compat["compatibility"]["compatibility"]}')
            ret.append(f'identified via: {compat["compatibility"]["identified_via"]}')
        else:
            ret.append(f'{compat["compatibility"]["compatibility"]}')
        return "\n".join(ret), None

    def format_compatibilities(self, compats, verbose=False):
        ret = []
        ret.append(f'{compats["compat_license"]}')
        if verbose:
            for compat in compats['compatibilities']:
                ret.append(f' * "{compat["queried_name"]}" -> "{compat["name"]}" via "{compat["identified_via"]}"')

        if compats['ambiguities']:
            warnings = f'Warnings: {", ".join(compats["ambiguities"])}'
        else:
            warnings = None

        return '\n'.join(ret), warnings

    def format_compat_list(self, all_compats, verbose=False):
        return '\n'.join([f'{comp["spdxid"]} -> {comp["compatibility_as"]}' for comp in all_compats]), None

    def __OBSOLETE_format_identified(self, identified, verbose=False):
        ret = []
        id_lic = identified['identified_element']
        ret.append(f'{id_lic["name"]}')
        if verbose:
            ret.append(f' * "{id_lic["queried_name"]}" -> "{id_lic["name"]}" via "{id_lic["identified_via"]}"')
        return "\n".join(ret)

    def format_expression(self, expression, verbose=False):
        ret = []
        id_lic = expression['identified_license']
        ret.append(f'{id_lic}')
        if verbose:
            for identification in expression['identifications']:
                ret.append(f' * "{identification["queried_name"]}" -> "{identification["name"]} via "{identification["identified_via"]}"')
        if expression['ambiguities']:
            warnings = f'Warnings: {", ".join(expression["ambiguities"])}'
        else:
            warnings = None
        return '\n'.join(ret), warnings

    def format_alias_list(self, all_aliases, verbose=False):
        return '\n'.join([f'{k} -> {v}' for k, v in all_aliases.items()]), None

    def format_licenses(self, licenses, verbose=False):
        licenses.sort()
        return '\n'.join(licenses), None

    def format_operators(self, operators, verbose=False):
        return '\n'.join([f'{k} -> {v}' for k, v in operators.items()]), None

    def format_error(self, error, verbose=False):
        return f'Error: {error}', None

    def format_license_complete(self, lic, verbose=False):
        ret_str = []
        ret_str.append(f'{lic["name"]}')
        ret_str.append(f'    spdxid:           {lic["spdxid"]}')
        ret_str.append(f'    spdx_url:         https://spdx.org/licenses/{lic["spdxid"]}.html')
        ret_str.append(f'    scancode_key:     {lic["scancode_key"]}')
        ret_str.append(f'    scancode_db_url:  https://scancode-licensedb.aboutcode.org/{lic["scancode_key"]}.html')
        ret_str.append(f'    aliases:          {", ".join(lic["aliases"])}')
        if 'compatibility_as' in lic:
            ret_str.append(f'    compatibility_as: {lic["compatibility_as"]}')
        if 'comment_as' in lic:
            ret_str.append(f'    comment:          {lic["comment"]}')

        return "\n".join(ret_str), None
