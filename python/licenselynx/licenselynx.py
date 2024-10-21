import json
from importlib import resources


class LicenseLynx:
    @staticmethod
    def map(license_name):
        try:
            # Use importlib.resources to read the JSON file
            with resources.open_text("licenselynx.resources", "merged_data.json") as file:
                merged_data = json.load(file)

            entry = merged_data.get(license_name)
            if entry:
                return LicenseObject(canonical=entry.get("canonical"), src=entry.get("src"))
            else:
                return None
        except Exception as e:
            return {"error": f"Error reading or parsing file: {str(e)}"}


class LicenseObject:
    def __init__(self, canonical, src):
        self.canonical = canonical
        self.src = src
