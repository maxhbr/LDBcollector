import json
import os
from collections import Counter
from src.validate.data_validation import extract_license_list_with_semver, build_dict_with_base_name_license, DATA_DIR, JSON_EXTENSION


def _get_non_unique(numbers):
    counts = Counter(numbers)
    return [num for num, count in counts.items() if count > 1]


def _identify_major_only_licenses(base_name_dict):
    major_version_only_license_list = []
    not_major_version_only_license_list = []
    for base_name, licenses in base_name_dict.items():
        major_list = list()
        for license in licenses:
            major = license[1]

            major_list.append(major)

        duplicate_major_versions = _get_non_unique(major_list)
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


def _update_flag_in_licence_files(major_version_only_license_list, not_major_version_only_license_list):
    _write_to_license_file(major_version_only_license_list, is_major_version_only=True)
    _write_to_license_file(not_major_version_only_license_list, is_major_version_only=False)


def _write_to_license_file(canonical_license_list, is_major_version_only=False):
    for license in canonical_license_list:
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'r') as f:
            json_data = json.load(f)
            json_data['isMajorVersionOnly'] = is_major_version_only
        with open(os.path.join(DATA_DIR, str(license + JSON_EXTENSION)), 'w') as f:
            json.dump(json_data, f, indent=4)


def main():
    licenses_list = []
    extract_license_list_with_semver(licenses_list)

    base_name_dict = build_dict_with_base_name_license(licenses_list)

    major_version_only_license_list, not_major_version_only_license_list = _identify_major_only_licenses(base_name_dict)

    _update_flag_in_licence_files(major_version_only_license_list, not_major_version_only_license_list)


if __name__ == "__main__":
    main()
