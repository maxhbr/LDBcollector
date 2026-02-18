#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
from unittest.mock import patch, mock_open
import pytest

from src.statistics.update_readme import (
    load_license_data,
    format_number,
    main,
)

# Sample JSON data for testing
sample_license_data = {
    "stableMap": {
        "1": {"id": "MIT"},
        "2": {"id": "Apache 2.0"},
        "3": {"id": "MIT"},
        "4": {"id": "GPL 3.0"},
        "5": {"id": "MIT"},
        "6": {"id": "Apache 2.0"}
    },
    "riskyMap": {}
}


def test_load_license_data():
    # Mock opening a file and loading JSON
    with patch("builtins.open", mock_open(read_data=json.dumps(sample_license_data))):
        data = load_license_data('mock_path')
        assert data == sample_license_data


def test_format_number():
    # Test whole thousands (should not have decimal point)
    assert format_number(1000) == "1k"
    assert format_number(10000) == "10k"
    assert format_number(5000) == "5k"

    # Test non-whole thousands (should have 1 decimal place)
    assert format_number(1500) == "1.5k"
    assert format_number(2500) == "2.5k"
    assert format_number(1100) == "1.1k"
    # 1999 rounds to 2.0k, but trailing .0 is removed
    assert format_number(1999) == "2k"

    # Test numbers less than 1000 (should stay as-is)
    assert format_number(500) == "500"
    assert format_number(999) == "999"
    assert format_number(1) == "1"
    assert format_number(0) == "0"


def test_main_prints_formatted_number():
    # Mock load_license_data to return sample data
    with patch("src.statistics.update_readme.load_license_data", return_value=sample_license_data), \
         patch("builtins.print") as mock_print:
        main()
        # Check that print was called with the formatted number
        # sample_license_data has 6 stableMap entries and 0 riskyMap entries = 6 total
        mock_print.assert_called_once_with("6")


if __name__ == "__main__":
    pytest.main()
