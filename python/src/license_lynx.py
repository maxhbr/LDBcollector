import json


class LicenseLynx:

    @staticmethod
    def map(license_name):
        try:
            with open('resources/merged_data.json', 'r') as file:
                merged_data = json.load(file)

                entry = merged_data.get(license_name)

                if entry:
                    # Create and return a LicenseObject with canonical and src
                    return LicenseObject(canonical=entry.get("canonical"), src=entry.get("src"))
                else:
                    return {"error": "License not found"}
        except FileNotFoundError:
            return {"error": "License not found"}


class LicenseObject:
    def __init__(self, canonical, src):
        self.canonical = canonical
        self.src = src
