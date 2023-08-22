import json
import yaml

OUTPUT_FORMAT_JSON = "Json"
OUTPUT_FORMAT_YAML = "Yaml"
OUTPUT_FORMAT_TEXT = "text"
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

    def format_identified_list(self, all_aliases, verbose):
        return None

class JsonOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return json.dumps(compat, indent=4)

    def format_compat_list(self, all_compats, verbose):
        return json.dumps(all_compats, indent=4)

    def format_identified(self, identified, verbose):
        return json.dumps(identified, indent=4)

    def format_identified_list(self, all_aliases, verbose):
        return json.dumps(all_aliases, indent=4)

class YamlOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return yaml.dump(compat)

    def format_compat_list(self, all_compats, verbose):
        return None

    def format_identified(self, identified, verbose):
        return yaml.dump(identified)

    def format_identified_list(self, all_aliases, verbose):
        return yaml.dump(all_aliases)

class TextOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        ret = []
        id_lic = compat["identified_license"]
        if verbose:
            ret.append(f'queried_name: {id_lic["queried_name"]}')
            ret.append(f'name: {id_lic["name"]}')
            ret.append(f'identified via: {id_lic["identified_via"]}')
            ret.append(f'compatibility as: {compat["compatibility_as"]}')
        else:
            ret.append(f'{compat["compatibility_as"]}')
        return "\n".join(ret)

    def format_compat_list(self, all_compats, verbose):
        ret = []
        for comp in all_compats:
            ret.append(f'{comp["spdxid"]} -> {comp["compatibility_as"]}')

        return "\n".join(ret)

    def format_identified(self, identified, verbose):
        ret = []
        id_lic = identified["identified_license"]
        if verbose:
            ret.append(f'queried_name: {id_lic["queried_name"]}')
            ret.append(f'name: {id_lic["name"]}')
            ret.append(f'identified via: {id_lic["identified_via"]}')
        else:
            ret.append(f'{id_lic["name"]}')
        return "\n".join(ret)

    def format_identified_list(self, all_aliases, verbose):
        ret = []
        for alias, value in all_aliases.items():
            ret.append(f'{alias} -> {value}')

        return "\n".join(ret)
