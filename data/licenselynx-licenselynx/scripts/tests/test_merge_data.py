#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import json
import os
import tempfile

import pytest
from src.load.merge_data import read_data, write_data, main, _build_maps_from_dir, read_org_data


@pytest.fixture
def data_dir(tmpdir):
    data = {
        "license1.json": {"canonical": {"id": "license1"}, "aliases": {"SPDX": ["lic1"], "custom": ["lic1_custom"]},
                          "risky": ["lic1_risky"]},
        "license2.json": {"canonical": {"id": "license2"}, "aliases": {"SPDX": ["lic2", "lic2_alt"]}}
    }
    for filename, content in data.items():
        filepath = tmpdir.join(filename)
        with open(filepath, 'w') as f:
            json.dump(content, f)
    return tmpdir


def test_read_data(data_dir):
    data = read_data(str(data_dir))
    print(data)
    assert len(data) == 2
    stable_map = "stableMap"
    assert len(data[stable_map]) == 6
    risky_map = "riskyMap"
    assert len(data[risky_map]) == 1

    assert "license1" in data[stable_map]
    assert "lic1" in data[stable_map]
    assert "lic1_custom" in data[stable_map]

    assert "license2" in data[stable_map]
    assert "lic2" in data[stable_map]
    assert "lic2_alt" in data[stable_map]

    assert "lic1_risky" in data[risky_map]


def test_write_data(tmpdir):
    alias_mapping = {"license1": "license1", "lic1": "license1"}
    output_path = tmpdir.join("test_output.json")
    write_data(alias_mapping, str(output_path))
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data == alias_mapping


@pytest.fixture
def temp_data_dir():
    # Create a temporary directory with JSON files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample JSON files
        license_1 = {
            "canonical": {
                "id": "MIT",
                "src": "spdx"
            },
            "aliases": {
                "source1": ["MIT License", "MIT Open Source License"],
                "source2": ["MIT"]
            },
        }

        license_2 = {
            "canonical": {
                "id": "GPL",
                "src": "spdx",
            },
            "aliases": {
                "source1": ["GNU General Public License", "GPL v3"],
                "source2": ["GPLv3"]
            },
            "risky": [
                "risky_gpl_3"
            ]
        }

        # Write the JSON data to file in the temp directory
        with open(os.path.join(temp_dir, 'license1.json'), 'w') as f:
            json.dump(license_1, f)

        with open(os.path.join(temp_dir, 'license2.json'), 'w') as f:
            json.dump(license_2, f)

        yield temp_dir  # This is the data directory


@pytest.fixture
def temp_output_file():
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        yield temp_file.name
    # Clean up after the test
    os.remove(temp_file.name)


def test_main_integration(temp_data_dir, temp_output_file, monkeypatch):
    # Mock the command-line arguments
    monkeypatch.setattr('sys.argv', ['data_validation', '--output', temp_output_file])

    # Set the DATA_DIR variable to the temporary data directory for testing
    monkeypatch.setattr('src.load.merge_data.DATA_DIR', temp_data_dir)

    # Call the main function
    main()

    # Check the output file contents
    with open(temp_output_file, 'r') as f:
        output_data = json.load(f)

    # Expected alias mappings
    expected_output = {
        "stableMap": {
            "MIT": {
                "id": "MIT",
                "src": "spdx"
            },
            "MIT License": {
                "id": "MIT",
                "src": "spdx"
            },
            "MIT Open Source License": {
                "id": "MIT",
                "src": "spdx"
            },
            "GNU General Public License": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPL v3": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPLv3": {
                "id": "GPL",
                "src": "spdx"
            },
            "GPL": {
                "id": "GPL",
                "src": "spdx"
            },
        },
        'riskyMap': {
            "risky_gpl_3": {
                "id": "GPL",
                "src": "spdx"
            }
        }
    }

    assert output_data == expected_output


def test_build_maps_from_dir(tmpdir):
    license1 = {
        "canonical": {"id": "MIT"},
        "aliases": {"spdx": ["MIT License"]},
        "risky": ["mit-risky"]
    }
    license2 = {
        "canonical": {"id": "Apache-2.0"},
        "aliases": {"spdx": ["Apache License 2.0"], "custom": ["Apache2"]},
        "risky": ["apache-risky"]
    }
    with open(tmpdir.join("MIT.json"), 'w') as f:
        json.dump(license1, f)
    with open(tmpdir.join("Apache-2.0.json"), 'w') as f:
        json.dump(license2, f)

    canonical_dict, risky_dict = _build_maps_from_dir(str(tmpdir))

    # Canonical IDs present
    assert "MIT" in canonical_dict
    assert "Apache-2.0" in canonical_dict

    # Aliases present
    assert "MIT License" in canonical_dict
    assert "Apache License 2.0" in canonical_dict
    assert "Apache2" in canonical_dict

    # Canonical dict maps to correct objects
    assert canonical_dict["MIT"] == {"id": "MIT"}
    assert canonical_dict["MIT License"] == {"id": "MIT"}
    assert canonical_dict["Apache-2.0"] == {"id": "Apache-2.0"}

    # Risky entries
    assert "mit-risky" in risky_dict
    assert risky_dict["mit-risky"] == {"id": "MIT"}
    assert "apache-risky" in risky_dict
    assert risky_dict["apache-risky"] == {"id": "Apache-2.0"}


def test_build_maps_from_dir_skips_non_json(tmpdir):
    license1 = {
        "canonical": {"id": "MIT"},
        "aliases": {"spdx": ["MIT License"]},
        "risky": []
    }
    with open(tmpdir.join("MIT.json"), 'w') as f:
        json.dump(license1, f)
    with open(tmpdir.join("README.txt"), 'w') as f:
        f.write("This is not a JSON file")

    canonical_dict, risky_dict = _build_maps_from_dir(str(tmpdir))

    # Only JSON file processed
    assert "MIT" in canonical_dict
    assert "MIT License" in canonical_dict
    assert len(canonical_dict) == 2
    assert len(risky_dict) == 0


def test_read_org_data_single_org(tmpdir):
    org_dir = tmpdir.mkdir("orgs").mkdir("testOrg")
    license1 = {
        "canonical": {"id": "testOrgId", "src": "testOrg"},
        "aliases": {"custom": ["testOrg License"]},
        "isMajorVersionOnly": False,
        "rejected": [],
        "risky": ["testOrg-risky"]
    }
    with open(org_dir.join("testOrgId.json"), 'w') as f:
        json.dump(license1, f)

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    test_org_map = result["testOrg"]

    # Canonical ID present
    assert "testOrgId" in test_org_map
    assert test_org_map["testOrgId"] == {"id": "testOrgId", "src": "testOrg"}

    # Alias present
    assert "testOrg License" in test_org_map
    assert test_org_map["testOrg License"] == {"id": "testOrgId", "src": "testOrg"}

    # Risky entries merged into org map
    assert "testOrg-risky" in test_org_map
    assert test_org_map["testOrg-risky"] == {"id": "testOrgId", "src": "testOrg"}


def test_read_org_data_multiple_orgs(tmpdir):
    orgs_dir = tmpdir.mkdir("orgs")
    test_org_dir = orgs_dir.mkdir("testOrg")
    acme_dir = orgs_dir.mkdir("acme")

    test_org_license = {
        "canonical": {"id": "testOrgId", "src": "testOrg"},
        "aliases": {"custom": ["testOrg License"]},
        "risky": []
    }
    acme_license = {
        "canonical": {"id": "ACME-1.0", "src": "acme"},
        "aliases": {"custom": ["ACME License"]},
        "risky": []
    }
    with open(test_org_dir.join("testOrgId.json"), 'w') as f:
        json.dump(test_org_license, f)
    with open(acme_dir.join("ACME-1.0.json"), 'w') as f:
        json.dump(acme_license, f)

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    assert "acme" in result


def test_read_org_data_no_orgs_dir(tmpdir):
    result = read_org_data(str(tmpdir))
    assert result == {}


def test_read_org_data_empty_org(tmpdir):
    tmpdir.mkdir("orgs").mkdir("testOrg")

    result = read_org_data(str(tmpdir))

    assert "testOrg" in result
    assert result["testOrg"] == {}


def test_main_integration_with_orgs(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create main license files
        main_license = {
            "canonical": {"id": "MIT", "src": "spdx"},
            "aliases": {"source1": ["MIT License"]},
            "risky": ["mit-risky"]
        }
        with open(os.path.join(temp_dir, "MIT.json"), 'w') as f:
            json.dump(main_license, f)

        # Create org subdir with org license files
        org_dir = os.path.join(temp_dir, "orgs", "testOrg")
        os.makedirs(org_dir)
        org_license = {
            "canonical": {"id": "testOrgId", "src": "testOrg"},
            "aliases": {"custom": ["testOrg License"]},
            "risky": ["testOrg-risky"]
        }
        with open(os.path.join(org_dir, "testOrgId.json"), 'w') as f:
            json.dump(org_license, f)

        # Create temp output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_out:
            output_path = tmp_out.name

        try:
            monkeypatch.setattr('src.load.merge_data.DATA_DIR', temp_dir)
            monkeypatch.setattr('sys.argv', ['merge_data', '--output', output_path])
            main()

            with open(output_path, 'r') as f:
                output_data = json.load(f)

            assert "stableMap" in output_data
            assert "riskyMap" in output_data
            assert "testOrg" in output_data

            # Verify stableMap content
            assert "MIT" in output_data["stableMap"]
            assert "MIT License" in output_data["stableMap"]

            # Verify riskyMap content
            assert "mit-risky" in output_data["riskyMap"]

            # Verify testOrg content (canonical + aliases + risky merged)
            assert "testOrgId" in output_data["testOrg"]
            assert "testOrg License" in output_data["testOrg"]
            assert "testOrg-risky" in output_data["testOrg"]
        finally:
            os.remove(output_path)


if __name__ == '__main__':
    pytest.main()
