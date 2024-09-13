import json
import pytest
from src.load.merge_data import read_data, write_data


@pytest.fixture
def data_dir(tmpdir):
    data = {
        "license1.json": {"canonical": "license1", "aliases": {"SPDX": ["lic1"], "custom": ["lic1_custom"]}},
        "license2.json": {"canonical": "license2", "aliases": {"SPDX": ["lic2", "lic2_alt"]}}
    }
    for filename, content in data.items():
        filepath = tmpdir.join(filename)
        with open(filepath, 'w') as f:
            json.dump(content, f)
    return tmpdir


def test_read_data(data_dir):
    data = read_data(str(data_dir))
    print(data)
    assert len(data) == 6
    assert "license1" in data
    assert "lic1" in data
    assert "lic1_custom" in data

    assert "license2" in data
    assert "lic2" in data
    assert "lic2_alt" in data


def test_write_data(tmpdir):
    alias_mapping = {"license1": "license1", "lic1": "license1"}
    output_path = tmpdir.join("test_output.json")
    write_data(alias_mapping, str(output_path))
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data == alias_mapping


if __name__ == '__main__':
    pytest.main()
