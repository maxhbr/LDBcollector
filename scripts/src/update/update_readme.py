import json
from collections import Counter


def load_license_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def count_canonical_licenses(license_data):
    return Counter(entry['canonical'] for entry in license_data.values())


def prepare_top_licenses_text(canonical_counts):
    top_canonical = canonical_counts.most_common(5)
    return top_canonical


def generate_svg(total_mappings, total_number_licenses, top_licenses, is_dark_mode=False):
    # Define colors for light and dark modes
    if is_dark_mode:
        background_color = "#1e1e1e"  # Dark background
        text_color = "#ffffff"  # White text
        accent_color = "#4caf50"  # Bright green for top licenses
    else:
        background_color = "#ffffff"  # Light background
        text_color = "#333333"  # Dark grey text
        accent_color = "#007bff"  # Soft blue for top licenses

    # Generate the top licenses section
    license_text = "".join(
        f'<text x="30" y="{180 + i * 30}" font-family="Arial, sans-serif" '
        f'font-size="18" fill="{accent_color}">{name}: <tspan font-weight="bold">{count}</tspan></text>'
        for i, (name, count) in enumerate(top_licenses)
    )

    # Read SVG template and format it
    with open("resources/template.svg") as f:
        svg_template = f.read().format(
            background_color=background_color,
            text_color=text_color,
            total_mappings=total_mappings,
            total_number_licenses=total_number_licenses,
            license_text=license_text
        )

    return svg_template


def save_svg(svg_content, file_path):
    with open(file_path, 'w') as f:
        f.write(svg_content)


def update_readme(license_data_file_path, svg_file_path):
    # Load license data
    license_data = load_license_data(license_data_file_path)

    # Count mappings and prepare SVG update
    total_mappings = len(license_data)

    canonical_counts = count_canonical_licenses(license_data)
    top_licenses = prepare_top_licenses_text(canonical_counts)

    total_number_licenses = len(canonical_counts)

    # Generate and save SVG
    svg_content = generate_svg(total_mappings, total_number_licenses, top_licenses, is_dark_mode=True)
    save_svg(svg_content, svg_file_path)

    print("SVG updated successfully.")


def main():
    update_readme("merged_data.json", "../../../stats.svg")


if __name__ == '__main__':
    main()
