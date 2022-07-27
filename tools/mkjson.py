#!/usr/bin/python3
#
# Generate a JSON file of all of the TOML data.
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

allowed_values = [
    "allowed",
    "allowed-content",
    "allowed-documentation",
    "allowed-fonts",
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
        data = toml.load(licensefile.path)

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

        for s in status:
            if s in allowed_values:
                approved = "yes"
            elif s == "not-allowed":
                approved = "no"

        # field: 'spdx_abbrev'
        spdx_abbrev = data["license"]["expression"]

        if "fedora" in keys:
            fedora_keys = [*data["fedora"]]

            # field: 'fedora_abbrev'
            if "abbreviation" in fedora_keys:
                fedora_abbrevs = data["fedora"]["abbreviation"]

            # field: 'fedora_name' (could be a list)
            if "name" in fedora_keys:
                fedora_names = data["fedora"]["name"]

        # sanity check
        assert isinstance(approved, str), \
               'approved is not string ({})'.format(licensefile)
        assert isinstance(fedora_names, str) or isinstance(fedora_names, list) or \
               ("not-allowed" in status), \
               'name in [fedora] section is neither string nor list ({})'.format(licensefile)
        assert ((isinstance(fedora_abbrevs, str) or isinstance(fedora_abbrevs, list)) or \
                ("not-allowed" in status)
               ), \
               '{} does not have fedora_abbrevs or is not-allowed'.format(licensefile)
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

    # write out the license data
    rawdata = json.JSONEncoder().encode(licensedata)
    parsed = json.loads(rawdata)

    with open(outputfile, "w") as f:
        f.write(json.dumps(parsed, indent=4, sort_keys=False))
