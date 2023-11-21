import re
import argparse

def sort_yaml_blocks(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    prefix = []
    blocks = []
    block = []
    comments = []
    in_categorizations = False

    for line in lines:
        if "categorizations:" in line:
            in_categorizations = True
            prefix.append(line)
            continue

        if not in_categorizations:
            prefix.append(line)
            continue

        if re.match(r"\s*#", line):
            comments.append(line)
        elif re.match(r"\s*- id:", line):
            if block:  # Add non-empty block to blocks
                blocks.append("".join(block))
            block = comments + [line]
            comments = []
        else:
            block.append(line)

    # Add the last block if it's non-empty
    if block:
        blocks.append("".join(block))

    def sorting_key(x):
        match = re.search(r'- id: "(.*)"', x)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Sorting key not found in block:\n{x}")

    try:
        blocks.sort(key=sorting_key)
    except ValueError as e:
        print(f"Exception while sorting: {e}")

    with open(output_file, 'w') as f:
        f.writelines(prefix)
        f.writelines(blocks)

def main():
    parser = argparse.ArgumentParser(description="Sort licenses based on 'id' field within 'categorizations'.")
    parser.add_argument('input_file', type=str, help='Input YAML file, usually license-classifications.yml')
    parser.add_argument('output_file', type=str, help='Output YAML file after sorting. Once verified, you can replace the current license-classifications.yml with this file.')

    args = parser.parse_args()

    sort_yaml_blocks(args.input_file, args.output_file)

if __name__ == "__main__":
    main()