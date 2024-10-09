import argparse
import json
import os

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(os.path.join(script_dir, '../../../data'))


def read_data(data_dir):
    data = {}
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r') as f:
                license_data = json.load(f)
                canonical_name = license_data.get("canonical")
                src = license_data.get("src")
                aliases = license_data.get("aliases", [])
                data[canonical_name] = {"canonical": canonical_name, "src": src}
                for source in aliases:
                    for alias in aliases[source]:
                        data[alias] = {"canonical": canonical_name, "src": src}
    return data


def write_data(alias_mapping, output_path):
    with open(output_path, 'w') as outfile:
        json.dump(alias_mapping, outfile, indent=4)


def merge_data_to_paths(data_dir, output_path):
    data = read_data(data_dir)

    write_data(data, output_path)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', '-o', required=True, type=str, help='Path for export file')

    args = parser.parse_args(argv)

    output_path = args.output

    merge_data_to_paths(DATA_DIR, output_path)


if __name__ == '__main__':
    main()
