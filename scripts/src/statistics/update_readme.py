#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json


def load_license_data(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)


def format_number(num: int) -> str:
    """Format a number with 'k' suffix for thousands.

    Args:
        num: The number to format
    Returns:
        Formatted string (e.g., 10000 -> "10k", 1500 -> "1.5k", 500 -> "500")
    """
    if num >= 1000:
        formatted = num / 1000
        # Round to 1 decimal place and remove trailing ".0"
        result = f"{formatted:.1f}k"
        if result.endswith(".0k"):
            result = result[:-3] + "k"
        return result
    return str(num)


def main() -> None:
    license_data = load_license_data("merged_data.json")

    # Calculate total mappings
    risky_mappings = license_data['riskyMap']
    canonical_mappings = license_data['stableMap']
    total_mappings = len(risky_mappings) + len(canonical_mappings)

    # Format and print the result
    formatted_number = format_number(total_mappings)
    print(formatted_number)


if __name__ == '__main__':
    main()
