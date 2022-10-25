#!/usr/bin/python3
#
# Validate license data files to ensure they conform to the TEMPLATE.toml
# rules.
#
# Author:  David Cantrell <dcantrell@redhat.com>
#
# Copyright (c) 2022 Red Hat, Inc.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

try:
    import tomllib as toml_module # Python 3.11+ standard library
    toml_mode = "rb"
except ImportError:
    import toml as toml_module
    toml_mode = "r"

status_values = [
    "allowed",
    "allowed-content",
    "allowed-documentation",
    "allowed-fonts",
    "allowed-firmware",
    "not-allowed",
]


def usage(prog):
    print("Usage: %s [license data directory]" % prog)
    sys.exit(1)


if __name__ == "__main__":
    r = 0
    prog = os.path.basename(sys.argv[0])

    if len(sys.argv) != 2:
        usage(prog)

    datadir = os.path.realpath(sys.argv[1])

    if not os.path.isdir(datadir):
        usage(prog)

    for licensefile in os.scandir(datadir):
        # all license data files must be *.toml files
        if not licensefile.name.endswith(".toml"):
            sys.stderr.write(
                "*** %s license file does not end with '.toml'\n" % licensefile.name  # noqa: E501
            )
            r = 1
            continue

        # read in the data file
        with open(licensefile.path, toml_mode) as f:
            data = toml_module.load(f)

        # check the top level keys
        # the license key is required, the fedora key can exist
        # all other keys are invalid at this level
        keys = [*data]

        if "license" not in keys:
            sys.stderr.write("*** %s missing the [license] block\n" % licensefile.name)  # noqa: E501
            r = 1
        else:
            keys.remove("license")

        if "fedora" in keys:
            # the fedora key is allowed, but not required
            keys.remove("fedora")

        if len(keys) != 0:
            for key in keys:
                sys.stderr.write(
                    "*** %s contains invalid [%s] block\n" % licensefile.name
                )
                r = 1

        # check the license key
        keys = [*data["license"]]

        if "expression" not in keys or not isinstance(
            data["license"]["expression"], str
        ):
            sys.stderr.write(
                "*** %s missing the 'expression' key in the [license] block\n"
                % licensefile.name
            )
            r = 1
        else:
            keys.remove("expression")

        if "status" not in keys:
            sys.stderr.write(
                "*** %s missing the 'status' key in the [license] block\n"
                % licensefile.name
            )
            r = 1
        else:
            status = data["license"]["status"]

            if isinstance(status, str) and status not in status_values:
                sys.stderr.write(
                    "*** %s has invalid 'status' in the [license] block: %s\n"
                    % (licensefile.name, status)
                )
                r = 1
            elif isinstance(status, list):
                if "not-allowed" in status and len(status) > 1:
                    sys.stderr.write(
                        "*** %s has 'not-allowed' status combined with other status in the [license] block\n"  # noqa: E501
                        % licensefile.name
                    )
                    r = 1

                for s in status_values:
                    if s in status:
                        status.remove(s)

                if len(status) != 0:
                    sys.stderr.write(
                        "*** %s has invalid status values in the [license] block: %s\n"  # noqa: E501
                        % (licensefile.name, status)
                    )
                    r = 1
            else:
                sys.stderr.write(
                    "*** %s has invalid 'status' in the [license] block\n"
                    % licensefile.name
                )
                r = 1

            keys.remove("status")

        if "url" in keys:
            if not isinstance(data["license"]["url"], str):
                sys.stderr.write(
                    "*** %s has 'url' value not of string type in the [license] block\n"  # noqa: E501
                    % licensefile.name
                )
                r = 1

            keys.remove("url")

        if "usage" in keys:
            if not isinstance(data["license"]["usage"], str):
                sys.stderr.write(
                    "*** %s has 'usage' value not of string type in the [license] block\n"  # noqa: E501
                    % licensefile.name
                )
                r = 1

            keys.remove("usage")
                
        if "text" in keys:
            if not isinstance(data["license"]["text"], str):
                sys.stderr.write(
                    "*** %s has 'text' value not of string type in the [license] block\n"  # noqa: E501
                    % licensefile.name
                )
                r = 1

            keys.remove("text")

        if len(keys) != 0:
            for key in keys:
                sys.stderr.write(
                    "*** %s contains invalid '%s' key in the [license] block\n"
                    % (licensefile.name, key)
                )
                r = 1

        # check the fedora key
        if "fedora" in keys:
            keys = [*data["fedora"]]

            if "legacy-name" in keys:
                legacy_name = data["fedora"]["legacy-name"]

                if not isinstance(legacy_name, list) and not isinstance(legacy_name, str):
                    sys.stderr.write(
                        "*** %s has 'name' value in the [fedora] block, but not a list or string\n"  # noqa: E501
                        % licensefile.name
                    )
                    r = 1

                keys.remove("legacy-name")

            if "legacy-abbreviation" in keys:
                legacy_abbreviation = data["fedora"]["legacy-abbreviation"]

                if not isinstance(legacy_abbreviation, list) and not isinstance(legacy_abbreviation, str):  # noqa: E501
                    sys.stderr.write(
                        "*** %s has 'legacy-abbreviation' value in the [fedora] block, but not a list or string\n"  # noqa: E501
                        % licensefile.name
                    )
                    r = 1

                keys.remove("legacy-abbreviation")

            if "notes" in keys:
                if not isinstance(data["fedora"]["notes"], str):
                    sys.stderr.write(
                        "*** %s has 'notes' value not of string type in the [fedora] block\n"  # noqa: E501
                        % licensefile.name
                    )
                    r = 1

                keys.remove("notes")

            if len(keys) != 0:
                for key in keys:
                    sys.stderr.write(
                        "*** %s contains invalid '%s' key in the [fedora] block\n"
                        % (licensefile.name, key)
                    )
                    r = 1

    sys.exit(r)
