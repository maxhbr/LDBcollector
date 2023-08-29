# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import yaml

OUTPUT_FORMAT_JSON = 'Json'
OUTPUT_FORMAT_YAML = 'Yaml'
OUTPUT_FORMAT_TEXT = 'text'
OUTPUT_FORMATS = [OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_YAML, OUTPUT_FORMAT_TEXT]

class OutputFormatterFactory():

    @staticmethod
    def formatter(format):
        if format.lower() == OUTPUT_FORMAT_JSON.lower():
            return JsonOutputFormatter()
        elif format.lower() == OUTPUT_FORMAT_YAML.lower():
            return YamlOutputFormatter()
        elif format.lower() == OUTPUT_FORMAT_TEXT.lower():
            return TextOutputFormatter()

class OutputFormatter():

    def format_compat(self, compat, verbose):
        return None

    def format_compat_list(self, all_compats, verbose):
        return None

    def format_identified(self, identified, verbose):
        return None

    def format_expression(self, expression, verbose):
        return None

    def format_identified_list(self, all_aliases, verbose):
        return None

    def format_error(self, message, verbose):
        return None

    def format_licenses(self, licenses, verbose):
        return None

    def format_compatibilities(self, compats, verbose):
        return None

    def format_operators(self, operators, verbose):
        return None

class JsonOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return json.dumps(compat, indent=4)

    def format_compat_list(self, all_compats, verbose):
        return json.dumps(all_compats, indent=4)

    def format_identified(self, identified, verbose):
        return json.dumps(identified, indent=4)

    def format_expression(self, expression, verbose):
        return json.dumps(expression, indent=4)

    def format_identified_list(self, all_aliases, verbose):
        return json.dumps(all_aliases, indent=4)

    def format_error(self, error, verbose):
        return json.dumps({'error': f'{error}'}, indent=4)

    def format_licenses(self, licenses, verbose):
        return json.dumps(licenses, indent=4)

    def format_compatibilities(self, compats, verbose):
        return json.dumps(compats)

    def format_operators(self, operators, verbose):
        return json.dumps(operators)

class YamlOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return yaml.dump(compat)

    def format_compat_list(self, all_compats, verbose):
        return None

    def format_identified(self, identified, verbose):
        return yaml.dump(identified)

    def format_expression(self, expression, verbose):
        return yaml.dump(expression)

    def format_identified_list(self, all_aliases, verbose):
        return yaml.dump(all_aliases)

    def format_error(self, error, verbose):
        return yaml.dump({'error': f'{error}'})

    def format_licenses(self, licenses, verbose):
        return yaml.dump(licenses)

    def format_compatibilities(self, compats, verbose):
        return yaml.dump(compats)

    def format_operators(self, operators, verbose):
        return yaml.dump(operators)

class TextOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
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
        return "\n".join(ret)

    def format_compatibilities(self, compats, verbose):
        ret = []
        ret.append(f'{compats["compat_license"]}')
        if verbose:
            for compat in compats['compatibilities']:
                lic_id = compat["license_identification"]
                lic_elem = lic_id["identified_element"]
                if lic_elem["identified_via"] == 'operator':
                    ret.append(f' * "{lic_elem["queried_name"]}" -> "{lic_elem["name"]}" via "{lic_elem["identified_via"]}"')
                else:
                    ret.append(f' * "{lic_elem["queried_name"]}" -> "{lic_elem["name"]}" via "{lic_elem["identified_via"]}" -> "{compat["name"]}" via "{compat["compat_identification"]["compatibility"]["identified_via"]}"')

        return '\n'.join(ret)

    def format_compat_list(self, all_compats, verbose):
        return '\n'.join([ f'{comp["spdxid"]} -> {comp["compatibility_as"]}' for comp in all_compats ])

    def format_identified(self, identified, verbose):
        ret = []
        id_lic = identified['identified_element']
        ret.append(f'{id_lic["name"]}')
        if verbose:
            ret.append(f' * "{id_lic["queried_name"]}" -> "{id_lic["name"]}" via "{id_lic["identified_via"]}"')
        return "\n".join(ret)

    def format_expression(self, expression, verbose):
        ret = []
        id_lic = expression['identified_license']
        ret.append(f'{id_lic}')
        if verbose:
            for identification in expression['identifications']:
                id_elem = identification['identified_element']
                ret.append(f' * "{id_elem["queried_name"]}" -> "{id_elem["name"]} via "{id_elem["identified_via"]}"')
        return '\n'.join(ret)

    def format_identified_list(self, all_aliases, verbose):
        return '\n'.join([ f'{k} -> {v}'  for k, v in all_aliases.items() ])

    def format_licenses(self, licenses, verbose):
        licenses.sort()
        return '\n'.join(licenses)

    def format_operators(self, operators, verbose):
        return '\n'.join([ f'{k} -> {v}'  for k, v in operators.items() ])

    def format_error(self, error, verbose):
        return f'Error, {error}'
