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
    import tomllib
except ImportError:
    import tomli as tomllib

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
    i, licensedata, approved, fedora_names, fedora_abbrev, spdx_abbrev, url, usage, text
):
    licensedata[i] = {
        "license": {
            "expression": spdx_abbrev,
            "status": approved,
        },
        "fedora": {
            "legacy-name": fedora_names,
            "legacy-abbreviation": fedora_abbrev,
        },
    }
    if url:
        licensedata[i]["license"]["url"] = url
    if usage:
        licensedata[i]["license"]["usage"] = usage
    if text:
        licensedata[i]["license"]["text"] = text

    # DEPRECATED part
    if isinstance(fedora_abbrev, str):
        fedora_abbrev = [fedora_abbrev, ]
    for one_fedora_abbrev in fedora_abbrev:
        if i not in licensedata.keys():
            licensedata[i]= {}
        if isinstance(fedora_names, str):
            licensedata[i].update({
                "approved": approved,
                "fedora_abbrev": one_fedora_abbrev,
                "fedora_name": fedora_names,
                "spdx_abbrev": spdx_abbrev,
            })
            i += 1
        elif isinstance(fedora_names, list):
            for n in fedora_names:
                if n == "":
                    continue
                if i not in licensedata.keys():
                    licensedata[i]= {}
                licensedata[i].update({
                    "approved": approved,
                    "fedora_abbrev": one_fedora_abbrev,
                    "fedora_name": n,
                    "spdx_abbrev": spdx_abbrev,
                })
                i += 1
        else:
            licensedata[i].update({
                "approved": approved,
                "fedora_abbrev": one_fedora_abbrev,
                "fedora_name": "",
                "spdx_abbrev": spdx_abbrev,
            })
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
        with open(licensefile.path, "rb") as f:
            data = tomllib.load(f)

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
        url = data["license"].get("url")
        if url:
            url = url.strip()
        usage = data["license"].get("usage")
        if usage:
            usage = usage.strip()
        text = data["license"].get("text")
        if text:
            text = text.strip()

        approved = "yes" if status and all(s in allowed_values for s in status) else "no"

        # field: 'spdx_abbrev'
        spdx_abbrev = data["license"]["expression"]

        if "fedora" in keys:
            fedora_keys = [*data["fedora"]]

            # field: 'fedora_abbrev'
            if "abbreviation" in fedora_keys:
                fedora_abbrevs = data["fedora"]["legacy-abbreviation"]

                assert ((isinstance(fedora_abbrevs, str) or isinstance(fedora_abbrevs, list)) or \
                        ("not-allowed" in status)
                       ), \
                       '{} does not have fedora_abbrevs or is not-allowed'.format(licensefile)

            # field: 'fedora_name' (could be a list)
            if "legacy-name" in fedora_keys:
                fedora_names = data["fedora"]["legacy-name"]

                assert isinstance(fedora_names, str) or isinstance(fedora_names, list) or \
                       ("not-allowed" in status), \
                       'legacy-name in [fedora] section is neither string nor list ({})'.format(licensefile)

        # sanity check
        assert isinstance(approved, str), \
               'approved is not string ({})'.format(licensefile)

        assert isinstance(spdx_abbrev, str), \
               'spdx_abbrev is not string ({})'.format(licensefile)

        # add these keys to the main hash table
        if isinstance(fedora_abbrevs, str) or isinstance(fedora_abbrevs, list):
            i = add_license_data(
                i, licensedata, approved, fedora_names, fedora_abbrevs, spdx_abbrev,
                status, url, usage, text  # noqa: E501
            )
        else:
            # Handle licenses with only an SPDX legacy-abbreviation, not a Fedora legacy-abbreviation
            licensedata[i] = {
                "approved": approved,
                "spdx_abbrev": spdx_abbrev,
                "license": {
                    "expression": spdx_abbrev,
                    "status": status,
                },
                "fedora": {},
            }
            if url:
                licensedata[i]["license"]["url"] = url
            if usage:
                licensedata[i]["license"]["usage"] = usage
            if text:
                licensedata[i]["license"]["text"] = text
            i += 1

    # write out the license data
    rawdata = json.JSONEncoder().encode(licensedata)
    parsed = json.loads(rawdata)

    with open(outputfile, "w") as f:
        f.write(json.dumps(parsed, indent=4, sort_keys=False))
