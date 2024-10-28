import json
from collections import Counter


def load_license_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def count_canonical_licenses(license_data):
    return Counter(entry['canonical'] for entry in license_data.values())


def prepare_top_licenses_text(canonical_counts):
    top_3_canonical = canonical_counts.most_common(5)
    return top_3_canonical


def generate_svg(total_mappings, top_licenses, is_dark_mode=False):
    # Define colors for light and dark modes
    if is_dark_mode:
        background_color = "#1e1e1e"  # Dark background
        text_color = "#ffffff"  # White text
        accent_color = "#4caf50"  # Bright green for top licenses
    else:
        background_color = "#ffffff"  # Light background
        text_color = "#333333"  # Dark grey text
        accent_color = "#007bff"  # Soft blue for top licenses

    # Create an SVG string without the header
    svg_template = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="300">
        <rect width="100%" height="100%" fill="{background_color}"/>

        <text x="30" y="60" font-family="Arial, sans-serif" font-size="24" fill="{text_color}">
            Total Mappings: <tspan font-weight="bold">{total_mappings}</tspan>
        </text>

        <text x="30" y="100" font-family="Arial, sans-serif" font-size="20" fill="{text_color}">
            Top Licenses:
        </text>
        {"".join([
        f'<text x="30" y="{140 + i * 30}" font-family="Arial, sans-serif" font-size="18" fill="{accent_color}">{name}: <tspan font-weight="bold">{count}</tspan></text>'
        for i, (name, count) in enumerate(top_licenses)
    ])}
    </svg>
    '''
    return svg_template


def save_svg(svg_content, file_path):
    with open(file_path, 'w') as f:
        f.write(svg_content)


def main(license_data_file_path, svg_file_path):
    # Load license data
    license_data = load_license_data(license_data_file_path)

    # Count mappings and prepare SVG update
    total_mappings = len(license_data)

    canonical_counts = count_canonical_licenses(license_data)
    top_licenses = prepare_top_licenses_text(canonical_counts)

    # Generate and save SVG
    svg_content = generate_svg(total_mappings, top_licenses, is_dark_mode=True)
    save_svg(svg_content, svg_file_path)

    print("SVG updated successfully.")


if __name__ == '__main__':
    main("merged_data.json", "../../../stats.svg")
