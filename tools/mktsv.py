#!/usr/bin/python3
#
# Generate a TSV file of all of the TOML data.
# This is for inclusion in Fedora Legal documentation, which is AsciiDoc.
#
# Author:  David Cantrell <dcantrell@redhat.com>
#
# Copyright (c) 2022 Red Hat, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#     3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
import json
import toml
import tsv

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
            columns.append("\"Y\"")
        else:
            columns.append("\"N\"")

    # the 6th column is the SPDX expression
    columns.append("\"%s\"" % data["license"]["expression"])

    # the 7th column is the old Fedora abbreviation
    # the 8th column is the old Fedora name
    # if these are missing, they are empty
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "abbreviation" in fedora_keys:
            alist = None

            for a in data["fedora"]["abbreviation"]:
                if alist is None:
                    alist = a
                else:
                    alist += "\n" + a

            columns.append("\"%s\"" % alist)
        else:
            columns.append("\"\"")

        if "name" in fedora_keys:
            nlist = None

            for n in data["fedora"]["name"]:
                if nlist is None:
                    nlist = n
                else:
                    nlist += "\n" + n

            columns.append("\"%s\"" % nlist)
        else:
            columns.append("\"\"")
    else:
        columns.append("\"\"")
        columns.append("\"\"")

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

    columns.append("\"%s\"" % url)

    # the 10th column is any fedora 'notes' field
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "notes" in fedora_keys:
            columns.append("\"%s\"" % " ".join(data["fedora"]["notes"].split()))
        else:
            columns.append("\"\"")
    else:
        columns.append("\"\"")

    allowed.list_line(columns)


def write_not_allowed(keys, notallowed):
    columns = []

    # the 1st column is the SPDX expression
    columns.append("\"%s\"" % data["license"]["expression"])

    # the 2nd column is the old Fedora name
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "name" in fedora_keys:
            nlist = None

            for n in data["fedora"]["name"]:
                if nlist is None:
                    nlist = n
                else:
                    nlist += "\n" + n

            columns.append("\"%s\"" % nlist)
        else:
            columns.append("\"\"")
    else:
        columns.append("\"\"")

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

    columns.append("\"%s\"" % url)

    # the 4th column is any fedora 'notes' field
    if "fedora" in keys:
        fedora_keys = [*data["fedora"]]

        if "notes" in fedora_keys:
            columns.append("\"%s\"" % " ".join(data["fedora"]["notes"].split()))
        else:
            columns.append("\"\"")
    else:
        columns.append("\"\"")

    notallowed.list_line(columns)


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

    allowed = tsv.TsvWriter(open(os.path.join(cwd, "allowed.tsv"), "w"))
    notallowed = tsv.TsvWriter(open(os.path.join(cwd, "not-allowed.tsv"), "w"))

    for licensefile in os.scandir(datadir):
        # all license data files must be *.toml files
        if not licensefile.name.endswith(".toml"):
            sys.stderr.write(
                "*** %s license file does not end with '.toml'\n" % licensefile.name  # noqa: E501
            )
            r = 1
            continue

        # read in the data file
        data = toml.load(licensefile.path)

        keys = [*data]
        license_keys = [*data["license"]]

        status = data["license"]["status"]
        if isinstance(status, str):
            status = [status]

        if "not-allowed" in status:
            write_not_allowed(keys, notallowed)
        else:
            write_allowed(keys, status, allowed)

    allowed.close()
    notallowed.close()
