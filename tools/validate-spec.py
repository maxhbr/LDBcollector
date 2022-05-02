#!/usr/bin/python3
#
# Validate license data files to ensure they conform to the TEMPLATE.toml
# rules.
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
import toml

status_values = [
    "approved",
    "approved-content",
    "approved-documentation",
    "approved-fonts",
    "not-approved",
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
        data = toml.load(licensefile.path)

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
                if "not-approved" in status and len(status) > 1:
                    sys.stderr.write(
                        "*** %s has 'not-approved' status combined with other status in the [license] block\n"  # noqa: E501
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
        keys = [*data["fedora"]]

        if "name" in keys:
            name = data["fedora"]["name"]

            if not isinstance(name, list) and not isinstance(name, str):
                sys.stderr.write(
                    "*** %s has 'name' value in the [fedora] block, but not a list or string\n"  # noqa: E501
                    % licensefile.name
                )
                r = 1

            keys.remove("name")

        if "abbreviation" in keys:
            abbreviation = data["fedora"]["abbreviation"]

            if not isinstance(abbreviation, list) and not isinstance(abbreviation, str):  # noqa: E501
                sys.stderr.write(
                    "*** %s has 'abbreviation' value in the [fedora] block, but not a list or string\n"  # noqa: E501
                    % licensefile.name
                )
                r = 1

            keys.remove("abbreviation")

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
