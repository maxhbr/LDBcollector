import json


class LicenseLynx:

    @staticmethod
    def map(license_name):
        try:
            with open('resources/merged_data.json', 'r') as file:
                merged_data = json.load(file)
                return merged_data.get(license_name, {"error": "License not found"})
        except FileNotFoundError:
            return {"error": "License not found"}
