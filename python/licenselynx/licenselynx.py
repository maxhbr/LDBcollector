import json
from importlib import resources


class LicenseLynx:
    @staticmethod
    def map(license_name: str):
        """
        Maps license name to the canonical license identifier
        :param license_name: string of a license name
        :return: LicenseObject with the canonical license identifier and source or None if no license is found
        """
        try:
            file_path = resources.files("licenselynx.resources").joinpath("merged_data.json")

            with file_path.open() as file:
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
