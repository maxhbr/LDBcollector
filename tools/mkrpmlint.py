#!/usr/bin/python3
#
# Generate an rpmlint config TOML file with ValidLicenses
#
# Author:  David Cantrell <dcantrell@redhat.com>
# Author:  Miro Hrončok <mhroncok@redhat.com>
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

try:
    import tomllib as toml_module # Python 3.11+ standard library
    toml_mode = "rb"
except ImportError:
    import toml as toml_module
    toml_mode = "r"

try:
    import tomli_w as toml_w_module
    toml_w_mode = "wb"
except ImportError:
    import toml as toml_w_module
    toml_w_mode = "w"

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
        with open(licensefile.path, toml_mode) as f:
            data = toml_module.load(f)

        keys = [*data]
        license_keys = [*data["license"]]

        status = None
        spdx_abbrev = None
        fedora_abbrevs = []

        # field: 'approved'
        status = data["license"]["status"]
        if isinstance(status, str):
            status = [status]

        for s in status:
            if s in allowed_values:
                approved = True
            elif s == "not-allowed":
                approved = False

        # field: 'spdx_abbrev'
        spdx_abbrev = data["license"]["expression"]

        if "fedora" in keys:
            fedora_keys = [*data["fedora"]]

            # field: 'fedora_abbrev'
            if "abbreviation" in fedora_keys:
                fedora_abbrevs = data["fedora"]["abbreviation"]

        if approved:
            if spdx_abbrev:
                spdx_abbrev, _, exception = spdx_abbrev.partition(" WITH ")
                if exception:
                    valid_exceptions_spdx.add(exception)
                valid_licenses_spdx.add(spdx_abbrev)
            # nb: remove this when we don't want the old licenses allowed by rmplint
            for fedora_abbrev in fedora_abbrevs:
                valid_licenses_legacy.add(fedora_abbrev)

    # write out the rpmlint toml files
    with open(outputfile_spdx, toml_w_mode) as f:
        comment_lines = "# File generated and owned by fedora-license-data\n"
        comment_lines += "# The SPDX license identifiers\n"
        if "b" in toml_w_mode:
            comment_lines = comment_lines.encode("utf-8")
        f.write(comment_lines)
        rpmlint_dict = {"ValidLicenses": sorted(valid_licenses_spdx),
                        "ValidLicenseExceptions": sorted(valid_exceptions_spdx)}
        toml_w_module.dump(rpmlint_dict, f)

    with open(outputfile_legacy, toml_w_mode) as f:
        comment_lines = "# File generated and owned by fedora-license-data\n"
        comment_lines += "# The legacy (callaway) license identifiers\n"
        if "b" in toml_w_mode:
            comment_lines = comment_lines.encode("utf-8")
        f.write(comment_lines)
        rpmlint_dict = {"ValidLicenses": sorted(valid_licenses_legacy)}
        toml_w_module.dump(rpmlint_dict, f)
