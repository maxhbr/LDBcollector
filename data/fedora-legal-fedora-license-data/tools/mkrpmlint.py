#!/usr/bin/python3
#
# Generate an rpmlint config TOML file with ValidLicenses
#
# Author:  David Cantrell <dcantrell@redhat.com>
# Author:  Miro Hrončok <mhroncok@redhat.com>
#
# Copyright (c) 2022 Red Hat, Inc.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w

allowed_values = [
    "allowed",
    "allowed-content",
    "allowed-documentation",
    "allowed-fonts",
    "allowed-firmware",
]


def usage(prog):
    print("Usage: %s [license data directory] [output spdx file] [output legacy file]" % prog)
    sys.exit(1)


if __name__ == "__main__":
    prog = os.path.basename(sys.argv[0])

    if len(sys.argv) != 4:
        usage(prog)

    datadir = os.path.realpath(sys.argv[1])
    outputfile_spdx = sys.argv[2]
    outputfile_legacy = sys.argv[3]

    if not os.path.isdir(datadir):
        usage(prog)

    valid_licenses_spdx = set()
    valid_exceptions_spdx = set()
    valid_licenses_legacy = set()

    for licensefile in os.scandir(datadir):
        # all license data files must be *.toml files
        if not licensefile.name.endswith(".toml"):
            sys.stderr.write(
                "*** %s license file does not end with '.toml'\n" % licensefile.name  # noqa: E501
            )
            continue

        # read in the data file
        with open(licensefile.path, "rb") as f:
            data = tomllib.load(f)

        keys = [*data]
        license_keys = [*data["license"]]

        status = None
        spdx_abbrev = None
        fedora_abbrevs = []

        # field: 'approved'
        status = data["license"]["status"]
        if isinstance(status, str):
            status = [status]

        if not status or any(s not in allowed_values for s in status):
            continue

        # field: 'spdx_abbrev'
        spdx_abbrev = data["license"]["expression"]

        if "fedora" in keys:
            fedora_keys = [*data["fedora"]]

            # field: 'fedora_abbrev'
            if "legacy-abbreviation" in fedora_keys:
                fedora_abbrevs = data["fedora"]["legacy-abbreviation"]

        if spdx_abbrev:
            spdx_abbrev, _, exception = spdx_abbrev.partition(" WITH ")
            if exception:
                valid_exceptions_spdx.add(exception)
            valid_licenses_spdx.add(spdx_abbrev)
        # nb: remove this when we don't want the old licenses allowed by rmplint
        for fedora_abbrev in fedora_abbrevs:
            valid_licenses_legacy.add(fedora_abbrev)

    # write out the rpmlint toml files
    with open(outputfile_spdx, "wb") as f:
        comment_lines = "# File generated and owned by fedora-license-data\n"
        comment_lines += "# The SPDX license identifiers\n"
        comment_lines = comment_lines.encode("utf-8")
        f.write(comment_lines)
        rpmlint_dict = {"ValidLicenses": sorted(valid_licenses_spdx),
                        "ValidLicenseExceptions": sorted(valid_exceptions_spdx)}
        tomli_w.dump(rpmlint_dict, f)

    with open(outputfile_legacy, "wb") as f:
        comment_lines = "# File generated and owned by fedora-license-data\n"
        comment_lines += "# The legacy (callaway) license identifiers\n"
        comment_lines = comment_lines.encode("utf-8")
        f.write(comment_lines)
        rpmlint_dict = {"ValidLicenses": sorted(valid_licenses_legacy)}
        tomli_w.dump(rpmlint_dict, f)
