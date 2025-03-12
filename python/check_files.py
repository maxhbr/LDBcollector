#
# SPDX-FileCopyrightText: Copyright 2025 Siemens AG
# SPDX-License-Identifier: Apache-2.0
#
import subprocess
import sys
import tarfile
import zipfile
import re
from pathlib import Path

EXPECTED_SUBPATHS = [
    "licenselynx/resources/merged_data.json",  # Without versioned directory
    ".+/licenselynx/resources/merged_data.json"  # With versioned directory (regex pattern)
]
DIST_DIR = Path("dist")


def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def get_latest_file(extension):
    """Get the latest file matching the given extension in the dist directory."""
    files = sorted(DIST_DIR.glob(f"*.{extension}"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print(f"Error: No {extension} file found in dist/")
        sys.exit(1)
    return files[0]


def find_matching_path(archive_members):
    """
    Check if any path in the archive matches one of the expected paths.
    """
    for expected_path in EXPECTED_SUBPATHS:
        if any(re.match(expected_path, member) for member in archive_members):
            return True
    return False


def check_sdist(file_path):
    """Check if the expected file exists in the tar.gz (sdist)."""
    with tarfile.open(file_path, "r:gz") as tar:
        archive_members = tar.getnames()
        if find_matching_path(archive_members):
            print("SUCCESS: merged_data.json found in source distribution.")
        else:
            print("ERROR: merged_data.json NOT found in source distribution.")
            sys.exit(1)


def check_wheel(file_path):
    """Check if the expected file exists in the wheel (.whl)."""
    with zipfile.ZipFile(file_path, "r") as zipf:
        archive_members = zipf.namelist()
        if find_matching_path(archive_members):
            print("SUCCESS: merged_data.json found in wheel distribution.")
        else:
            print("ERROR: merged_data.json NOT found in wheel distribution.")
            sys.exit(1)


def main():
    sdist_file = get_latest_file("tar.gz")
    wheel_file = get_latest_file("whl")

    check_sdist(sdist_file)
    check_wheel(wheel_file)

    print("All checks passed. Distributions are ready for release.")


if __name__ == "__main__":
    main()
