import json
import os

import pytest
from collections import Counter
from unittest.mock import patch, mock_open

# Assuming your main code is in a file named your_script.py
from src.update.update_readme import (
    load_license_data,
    count_canonical_licenses,
    prepare_top_licenses_text,
    generate_svg, main,  # Import the SVG generation function
)

# Sample JSON data for testing
sample_license_data = {
    "1": {"canonical": "MIT"},
    "2": {"canonical": "Apache 2.0"},
    "3": {"canonical": "MIT"},
    "4": {"canonical": "GPL 3.0"},
    "5": {"canonical": "MIT"},
    "6": {"canonical": "Apache 2.0"}
}

sample_readme_content = """
# Project Title

Total mappings: {{total_mappings}}

## Top Licenses
{{top_licenses}}
"""


def test_load_license_data():
    # Mock opening a file and loading JSON
    with patch("builtins.open", mock_open(read_data=json.dumps(sample_license_data))):
        data = load_license_data('mock_path')
        assert data == sample_license_data


def test_count_canonical_licenses():
    counts = count_canonical_licenses(sample_license_data)
    expected_counts = Counter({"MIT": 3, "Apache 2.0": 2, "GPL 3.0": 1})
    assert counts == expected_counts


def test_generate_svg_light_mode():
    svg_content = generate_svg(6, [("MIT", 3), ("Apache 2.0", 2), ("GPL 3.0", 1)], is_dark_mode=False)
    expected_svg_content = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="300">
        <rect width="100%" height="100%" fill="#ffffff"/>

        <text x="30" y="60" font-family="Arial, sans-serif" font-size="24" fill="#333333">
            Total Mappings: <tspan font-weight="bold">6</tspan>
        </text>

        <text x="30" y="100" font-family="Arial, sans-serif" font-size="20" fill="#333333">
            Top Licenses:
        </text>
        <text x="30" y="140" font-family="Arial, sans-serif" font-size="18" fill="#007bff">MIT: <tspan font-weight="bold">3</tspan></text><text x="30" y="170" font-family="Arial, sans-serif" font-size="18" fill="#007bff">Apache 2.0: <tspan font-weight="bold">2</tspan></text><text x="30" y="200" font-family="Arial, sans-serif" font-size="18" fill="#007bff">GPL 3.0: <tspan font-weight="bold">1</tspan></text>
    </svg>
    '''

    # Stripping whitespace for a fair comparison
    assert svg_content.strip() == expected_svg_content.strip()


def test_generate_svg_dark_mode():
    svg_content = generate_svg(6, [("MIT", 3), ("Apache 2.0", 2), ("GPL 3.0", 1)], is_dark_mode=True)
    expected_svg_content = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="300">
        <rect width="100%" height="100%" fill="#1e1e1e"/>

        <text x="30" y="60" font-family="Arial, sans-serif" font-size="24" fill="#ffffff">
            Total Mappings: <tspan font-weight="bold">6</tspan>
        </text>

        <text x="30" y="100" font-family="Arial, sans-serif" font-size="20" fill="#ffffff">
            Top Licenses:
        </text>
        <text x="30" y="140" font-family="Arial, sans-serif" font-size="18" fill="#4caf50">MIT: <tspan font-weight="bold">3</tspan></text><text x="30" y="170" font-family="Arial, sans-serif" font-size="18" fill="#4caf50">Apache 2.0: <tspan font-weight="bold">2</tspan></text><text x="30" y="200" font-family="Arial, sans-serif" font-size="18" fill="#4caf50">GPL 3.0: <tspan font-weight="bold">1</tspan></text>
    </svg>
    '''

    # Stripping whitespace for a fair comparison
    assert svg_content.strip() == expected_svg_content.strip()


def test_main_creates_svg_file():
    svg_file_path = 'mock_output.svg'

    # Mock the load_license_data and save_svg functions
    with patch("src.update.update_readme.load_license_data", return_value=sample_license_data), \
         patch("src.update.update_readme.save_svg") as mock_save_svg:
        # Call the main function
        main('mock_path', svg_file_path)

        # Check if save_svg was called with the correct arguments
        mock_save_svg.assert_called_once()

        # Get the argument passed to save_svg (svg content)
        svg_content = mock_save_svg.call_args[0][0]

        # Verify that the content includes expected values
        assert 'Total Mappings: <tspan font-weight="bold">6</tspan>' in svg_content
        assert 'MIT: <tspan font-weight="bold">3</tspan>' in svg_content

        # Optionally, you could also check if the file exists
        # For a true test, you would normally want to actually save and check for existence
        # Uncomment the following lines if you want to check file creation
        # with open(svg_file_path, 'r') as f:
        #     content = f.read()
        #     assert content == svg_content

    # Clean up the file after the test if it was created
    if os.path.exists(svg_file_path):
        os.remove(svg_file_path)


if __name__ == "__main__":
    pytest.main()
