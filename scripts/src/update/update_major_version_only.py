import json
import os
from collections import Counter
from src.validate.data_validation import extract_version_tokens
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../data'))
JSON_EXTENSION = ".json"


def main():
    licenses_list = []
    extract_license_list_with_semver(licenses_list)

    base_name_dict = build_dict_with_base_name_license(licenses_list)

    major_version_only_license_list, not_major_version_only_license_list = identify_major_only_licenses(base_name_dict)

    update_flag_in_licence_files(major_version_only_license_list, not_major_version_only_license_list)


def build_dict_with_base_name_license(licenses_list):
    base_name_dict = {}
    for name, version_set in licenses_list:
        if len(version_set) > 1:
            continue
        (version,) = version_set
        base_name = name.replace(version, '')
        if base_name not in base_name_dict:
            base_name_dict[base_name] = [(name, int(version.split(".")[0]))]
        else:
            base_name_dict[base_name].append((name, int(version.split(".")[0])))
    for base_name, versions in base_name_dict.copy().items():
        if len(versions) <= 1:
            base_name_dict.pop(base_name)
    return base_name_dict


def extract_license_list_with_semver(licenses_list):
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                canonical = data.get("canonical", [])

                canonical_tokens = extract_version_tokens(canonical)
                canonical_has_version = bool(canonical_tokens)
                if canonical_has_version:
                    canonical_and_version = (canonical, canonical_tokens)
                    licenses_list.append(canonical_and_version)


def identify_major_only_licenses(base_name_dict):
    major_version_only_license_list = []
    not_major_version_only_license_list = []
    for base_name, licenses in base_name_dict.items():
        major_list = list()
        for license in licenses:
            major = license[1]

            major_list.append(major)

        duplicate_major_versions = get_non_unique(major_list)
        if not duplicate_major_versions:
            for license in licenses:
                major_version_only_license_list.append(license[0])
        else:
            for license in licenses:
                if license[1] in duplicate_major_versions:
                    not_major_version_only_license_list.append(license[0])
                else:
                    major_version_only_license_list.append(license[0])
    return major_version_only_license_list, not_major_version_only_license_list


def update_flag_in_licence_files(major_version_only_license_list, not_major_version_only_license_list):
    for license in major_version_only_license_list:
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'r') as f:
            json_data = json.load(f)
            json_data['isMajorVersionOnly'] = True
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'w') as f:
            json.dump(json_data, f, indent=2)
    for license in not_major_version_only_license_list:
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'r') as f:
            json_data = json.load(f)
            json_data['isMajorVersionOnly'] = False
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'w') as f:
            json.dump(json_data, f, indent=2)


def get_non_unique(numbers):
    counts = Counter(numbers)
    return [num for num, count in counts.items() if count > 1]



if __name__ == "__main__":
    main()