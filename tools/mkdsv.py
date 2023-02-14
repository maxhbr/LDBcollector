#!/usr/bin/python3
#
# Generate a DSV file of all of the TOML data.
# This is for inclusion in Fedora Legal documentation, which is AsciiDoc.
#
# Author:  David Cantrell <dcantrell@redhat.com>
#
# Copyright (c) 2022 Red Hat, Inc.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import json
import csv

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
    print("Usage: %s [license data directory]" % prog)
    sys.exit(1)


def get_spdx_urls(expression):
    if expression.startswith("LicenseRef-"):
        return ""

    if expression.find(" ") == -1:
        return "https://spdx.org/licenses/%s.html" % expression

    tokens = expression.split(" ")
    r = None

    for token in tokens:
        if token.upper() in ["AND", "OR", "WITH"]:
            continue

        if r is None:
            r = "https://spdx.org/licenses/%s.html" % token
        else:
            r += "\nhttps://spdx.org/licenses/%s.html" % token

    return r


def write_allowed(keys, status, allowed):
    columns = []

    # allowed columns are the first 5 columns
    for v in allowed_values:
        if v in status:
            columns.append("Y")
        else:
            columns.append("")

    # the 6th column is the SPDX expression
    columns.append("%s" % data["license"]["expression"])

    # the 7th column is the old Fedora legacy-abbreviation
    # the 8th column is the old Fedora legacy-name
    # if these are missing, they are empty
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "legacy-abbreviation" in fedora_keys:
            alist = None

            for a in data["fedora"]["legacy-abbreviation"]:
                if alist is None:
                    alist = a
                else:
                    alist += "\n" + a

            columns.append("%s" % alist)
        else:
            columns.append("")

        if "legacy-name" in fedora_keys:
            nlist = None

            for n in data["fedora"]["legacy-name"]:
                if nlist is None:
                    nlist = n
                else:
                    nlist += "\n" + n

            columns.append("%s" % nlist)
        else:
            columns.append("")
    else:
        columns.append("")
        columns.append("")

    # the 9th column is any 'url' field plus URLs generated from the SPDX expression
    if "url" in keys:
        url = " ".join(data["license"]["url"].split())
    else:
        url = ""

    su = get_spdx_urls(data["license"]["expression"])

    if su != "":
        if url == "":
            url = su
        else:
            url += "\n" + get_spdx_urls(data["license"]["expression"])

    columns.append("%s" % url)

    allowed.writerow(columns)


def write_not_allowed(keys, notallowed):
    columns = []

    # the 1st column is the SPDX expression
    columns.append("%s" % data["license"]["expression"])

    # the 2nd column is the old Fedora legacy-name
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "legacy-name" in fedora_keys:
            nlist = None

            for n in data["fedora"]["legacy-name"]:
                if nlist is None:
                    nlist = n
                else:
                    nlist += "\n" + n

            columns.append("%s" % nlist)
        else:
            columns.append("")
    else:
        columns.append("")

    # the 3rd column is any 'url' field plus URLs generated from the SPDX expression
    if "url" in keys:
        url = " ".join(data["license"]["url"].split())
    else:
        url = ""

    su = get_spdx_urls(data["license"]["expression"])

    if su != "":
        if url == "":
            url = su
        else:
            url += "\n" + get_spdx_urls(data["license"]["expression"])

    columns.append("%s" % url)

    # the 4th column is any fedora 'usage' field
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "usage" in fedora_keys:
            columns.append("%s" % " ".join(data["fedora"]["usage"].split()))
        else:
            columns.append("")
    else:
        columns.append("")

    notallowed.writerow(columns)


if __name__ == "__main__":
    r = 0
    i = 0
    prog = os.path.basename(sys.argv[0])
    cwd = os.getcwd()

    if len(sys.argv) != 2:
        usage(prog)

    datadir = os.path.realpath(sys.argv[1])

    if not os.path.isdir(datadir):
        usage(prog)

    allowed_out = open(os.path.join(cwd, "allowed.dsv"), "w")
    allowed = csv.writer(allowed_out, delimiter='|')
    allowed.writerow(["Allowed", "Allowed Content", "Allowed Documentation", "Allowed Fonts", "Allowed Firmware", "SPDX Expression", "Fedora Abbreviation", "Full Name", "URL"])

    notallowed_out = open(os.path.join(cwd, "not-allowed.dsv"), "w")
    notallowed = csv.writer(notallowed_out, delimiter='|')
    notallowed.writerow(["SPDX Expression", "Full Name", "URL", "Usage"])

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

        status = data["license"]["status"]
        if isinstance(status, str):
            status = [status]

        if "not-allowed" in status:
            write_not_allowed(keys, notallowed)
        else:
            write_allowed(keys, status, allowed)

    allowed_out.close()
    notallowed_out.close()
