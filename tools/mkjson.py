#!/usr/bin/python3
#
# Generate a JSON file of all of the TOML data.
#
# Author:  David Cantrell <dcantrell@redhat.com>
#
# Copyright (c) 2022 Red Hat, Inc.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import json

try:
    import tomllib as toml_module # Python 3.11+ standard library
    toml_mode = "rb"
except ImportError:
    import toml as toml_module
    toml_mode = "r"

allowed_values = [
    "allowed",
    "allowed-content",
    "allowed-documentation",
    "allowed-fonts",
    "allowed-firmware",
]


def usage(prog):
    print("Usage: %s [license data directory] [output file]" % prog)
    sys.exit(1)


def add_license_data(
    i, licensedata, approved, fedora_names, fedora_abbrev, spdx_abbrev
):
    if isinstance(fedora_names, str):
        licensedata[i] = {
            "approved": approved,
            "fedora_abbrev": fedora_abbrev,
            "fedora_name": fedora_names,
            "spdx_abbrev": spdx_abbrev,
        }
        i += 1
    elif isinstance(fedora_names, list):
        for n in fedora_names:
            if n == "":
                continue
            licensedata[i] = {
                "approved": approved,
                "fedora_abbrev": fedora_abbrev,
                "fedora_name": n,
                "spdx_abbrev": spdx_abbrev,
            }
            i += 1
    else:
        licensedata[i] = {
            "approved": approved,
            "fedora_abbrev": fedora_abbrev,
            "fedora_name": "",
            "spdx_abbrev": spdx_abbrev,
        }
        i += 1

    return i


if __name__ == "__main__":
    r = 0
    i = 0
    prog = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        usage(prog)

    datadir = os.path.realpath(sys.argv[1])
    outputfile = sys.argv[2]

    if not os.path.isdir(datadir):
        usage(prog)

    licensedata = {}

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

        keys = [*data]
        license_keys = [*data["license"]]

        status = None
        spdx_abbrev = None
        fedora_abbrevs = None
        fedora_names = None

        # field: 'approved'
        status = data["license"]["status"]
        if isinstance(status, str):
            status = [status]

        approved = "yes" if status and all(s in allowed_values for s in status) else "no"

        # field: 'spdx_abbrev'
        spdx_abbrev = data["license"]["expression"]

        if "fedora" in keys:
            fedora_keys = [*data["fedora"]]

            # field: 'fedora_abbrev'
            if "abbreviation" in fedora_keys:
                fedora_abbrevs = data["fedora"]["abbreviation"]

                assert ((isinstance(fedora_abbrevs, str) or isinstance(fedora_abbrevs, list)) or \
                        ("not-allowed" in status)
                       ), \
                       '{} does not have fedora_abbrevs or is not-allowed'.format(licensefile)

            # field: 'fedora_name' (could be a list)
            if "name" in fedora_keys:
                fedora_names = data["fedora"]["name"]

                assert isinstance(fedora_names, str) or isinstance(fedora_names, list) or \
                       ("not-allowed" in status), \
                       'name in [fedora] section is neither string nor list ({})'.format(licensefile)

        # sanity check
        assert isinstance(approved, str), \
               'approved is not string ({})'.format(licensefile)

        assert isinstance(spdx_abbrev, str), \
               'spdx_abbrev is not string ({})'.format(licensefile)

        # add these keys to the main hash table
        if isinstance(fedora_abbrevs, str):
            i = add_license_data(
                i, licensedata, approved, fedora_names, fedora_abbrevs, spdx_abbrev  # noqa: E501
            )
        elif isinstance(fedora_abbrevs, list):
            for a in fedora_abbrevs:
                i = add_license_data(
                    i, licensedata, approved, fedora_names, a, spdx_abbrev
                )
        else:
            # Handle licenses with only an SPDX abbreviation, not a Fedora abbreviation
            licensedata[i] = {
                "approved": approved,
                "spdx_abbrev": spdx_abbrev,
            }
            i += 1

    # write out the license data
    rawdata = json.JSONEncoder().encode(licensedata)
    parsed = json.loads(rawdata)

    with open(outputfile, "w") as f:
        f.write(json.dumps(parsed, indent=4, sort_keys=False))
