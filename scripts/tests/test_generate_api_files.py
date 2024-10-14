import pytest
import json
import os
import tempfile
from src.web_api.generate_api_files import generate_hash, generate_files


@pytest.fixture
def temp_input_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump({
            "license/MIT": "MIT License",
            "license/GPL": "GNU General Public License"
        }, temp_file)
    yield temp_file.name
    os.unlink(temp_file.name)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_generate_hash():
    content = {"key": "value"}
    hash1 = generate_hash(content)
    assert isinstance(hash1, str)
    assert len(hash1) == 32  # MD5 hash is 32 characters long

    # Test that the same content produces the same hash
    hash2 = generate_hash(content)
    assert hash1 == hash2

    # Test that different content produces a different hash
    different_content = {"key": "different_value"}
    hash3 = generate_hash(different_content)
    assert hash1 != hash3


def test_generate_files_new_files(temp_input_file, temp_output_dir):
    generate_files(temp_input_file, temp_output_dir)

    # Check if files were created
    assert os.path.exists(os.path.join(temp_output_dir, 'license_MIT.json'))
    assert os.path.exists(os.path.join(temp_output_dir, 'license_GPL.json'))

    # Check the content of created files
    with open(os.path.join(temp_output_dir, 'license_MIT.json'), 'r') as f:
        content = json.load(f)
        assert content == {"canonical": "MIT License"}

    with open(os.path.join(temp_output_dir, 'license_GPL.json'), 'r') as f:
        content = json.load(f)
        assert content == {"canonical": "GNU General Public License"}


def test_generate_files_existing_unchanged(temp_input_file, temp_output_dir, capsys):
    # First run to create files
    generate_files(temp_input_file, temp_output_dir)

    captured = capsys.readouterr()
    assert "Creating" in captured.out

    # Second run to test unchanged files
    generate_files(temp_input_file, temp_output_dir)

    captured = capsys.readouterr()

    assert "No change for" in captured.out
    assert "Updating" not in captured.out
    assert "Creating" not in captured.out


def test_generate_files_existing_changed(temp_input_file, temp_output_dir, capsys):
    # First run to create files
    generate_files(temp_input_file, temp_output_dir)

    captured = capsys.readouterr()
    assert "Updating" not in captured.out
    assert "No change for" not in captured.out
    assert "Creating" in captured.out

    # Modify input file
    with open(temp_input_file, 'w') as f:
        json.dump({
            "license/MIT": "Modified MIT License",
            "license/GPL": "GNU General Public License"
        }, f)

    # Second run to test changed files
    generate_files(temp_input_file, temp_output_dir)

    captured = capsys.readouterr()
    assert "Updating" in captured.out
    assert "No change for" in captured.out
    assert "Creating" not in captured.out

    # Check the content of updated file
    with open(os.path.join(temp_output_dir, 'license_MIT.json'), 'r') as f:
        content = json.load(f)
        assert content == {"canonical": "Modified MIT License"}


def test_generate_files_invalid_input(temp_output_dir):
    with pytest.raises(FileNotFoundError):
        generate_files("non_existent_file.json", temp_output_dir)


if __name__ == '__main__':
    pytest.main()
