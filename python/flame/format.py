import json
import yaml

OUTPUT_FORMAT_JSON = "Json"
OUTPUT_FORMAT_YAML = "Yaml"
OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMATS = [ OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_YAML, OUTPUT_FORMAT_TEXT ]

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

    def format_compat_list(self):
        return None

    def format_alias(self):
        return None
    
    def format_alias_list(self):
        return None
    
class JsonOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return json.dumps(compat, indent=4)

    def format_compat_list(self):
        return None

    def format_alias(self):
        return None
    
    def format_alias_list(self):
        return None
    
class YamlOutputFormatter(OutputFormatter):

    def format_compat(self, compat, verbose):
        return yaml.dump(compat)

    def format_compat_list(self):
        return None

    def format_alias(self):
        return None
    
    def format_alias_list(self):
        return None
    
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

    def format_compat_list(self):
        return None

    def format_alias(self):
        return None
    
    def format_alias_list(self):
        return None
    
