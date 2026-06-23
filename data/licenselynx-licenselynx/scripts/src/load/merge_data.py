#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import argparse
import json
import os

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def _build_maps_from_dir(data_dir: str) -> tuple[dict, dict]:
    """
    Reads all JSON files in data_dir and returns two dicts:
      - canonical_dict: canonical IDs + all aliases -> canonical object
      - risky_dict: risky entries -> canonical object

    Skips non-JSON files and subdirectories.
    """
    canonical_dict = {}
    risky_dict = {}

    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r') as f:
            license_data = json.load(f)
            canonical_id = license_data["canonical"]["id"]
            canonical_object = license_data["canonical"]
            aliases = license_data.get("aliases", [])

            canonical_dict[canonical_id] = canonical_object
            for source in aliases:
                for alias in aliases[source]:
                    canonical_dict[alias] = canonical_object

            risky_aliases = license_data.get("risky")
            if not risky_aliases:
                continue
            for element in risky_aliases:
                risky_dict[element] = canonical_object

    return canonical_dict, risky_dict


def read_data(data_dir: str) -> dict:
    canonical_dict, risky_dict = _build_maps_from_dir(data_dir)
    data = {"stableMap": canonical_dict, "riskyMap": risky_dict}
    return data


def read_org_data(data_dir: str) -> dict:
    """
    Auto-discovers org subdirectories under data_dir/orgs/ and builds
    one map per org.

    Returns:
        dict with keys matching org directory names (e.g. 'siemens'), each mapping
        canonical IDs + aliases + risky entries -> canonical object.
        Returns empty dict if orgs/ does not exist.
    """
    orgs_path = os.path.join(data_dir, 'orgs')
    if not os.path.isdir(orgs_path):
        return {}

    org_maps: dict = {}
    for org_name in os.listdir(orgs_path):
        org_dir_path = os.path.join(orgs_path, org_name)
        if not os.path.isdir(org_dir_path):
            continue
        canonical_dict, risky_dict = _build_maps_from_dir(org_dir_path)
        canonical_dict.update(risky_dict)
        org_maps[org_name] = canonical_dict

    return org_maps


def write_data(alias_mapping: dict, output_path: str):
    with open(output_path, 'w') as outfile:
        json.dump(alias_mapping, outfile, indent=4)


def merge_data_to_paths(data_dir: str, output_path: str):
    data = read_data(data_dir)
    org_data = read_org_data(data_dir)
    data.update(org_data)

    write_data(data, output_path)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', '-o', required=True, type=str, help='Path for export file')

    args = parser.parse_args(argv)

    output_path = args.output

    merge_data_to_paths(DATA_DIR, output_path)


if __name__ == '__main__':
    main()
