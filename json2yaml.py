#!/usr/bin/python3
#
# Quick and Dirty script to convert fedora.json to individual YAML
# files.  The script divides them out based on abbreviation preference.
# In order:
# 1) If the license has fedora_abbrev, that is used and it is written to
#    ./fedora_abbrev
# 2) If the license has spdx_abbrev and fedora_abbrev is empty, it is
#    written to ./spdx_abbrev
# 3) As a last resort, the license is written to ./other using the full
#    name that is the JSON key as the filename.
#
# David Cantrell <dcantrell@redhat.com>
#

import os
import sys
import json
import yaml

def usage(cmd):
    print("Usage: %s [json file]" % os.path.basename(cmd))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage(sys.argv[0])
        sys.exit(1)

    cwd = os.getcwd()

    with open(os.path.realpath(sys.argv[1]), "rb") as f:
        rawdata = f.read()

    data = json.loads(rawdata)

    # write out the entries based on the type of abbreviation
    for k in data.keys():
        entry = data[k]

        license = {"name": k}

        # XXX: this still doesn't trim the single quotes, unknown why
        if entry["approved"] not in ["", "''"]:
            license["approved"] = entry["approved"].replace("'", "")

        if entry["fedora_abbrev"] not in ["", "''"]:
            license["fedora_abbrev"] = entry["fedora_abbrev"].replace("'", "")

        if entry["fedora_name"] not in ["", "''"]:
            license["fedora_name"] = entry["fedora_name"].replace("'", "")

        if entry["spdx_abbrev"] not in ["", "''"] and entry["spdx_abbrev"].find("#No official SPDX support as of") == -1:
            license["spdx_abbrev"] = entry["spdx_abbrev"].replace("'", "")

        if entry["spdx_name"] not in ["", "''"] and entry["spdx_name"].find("#No official SPDX support as of") == -1:
            license["spdx_name"] = entry["spdx_name"].replace("'", "")

        if entry["url"] not in ["", "''"]:
            license["url"] = entry["url"].replace("'", "")

        if "fedora_abbrev" in license.keys():
            # entry has a Fedora abbreviation
            outdir = os.path.realpath(os.path.join(cwd, "fedora_abbrev"))
            outfile = "%s.yaml" % license["fedora_abbrev"]
        elif "spdx_abbrev" in license.keys() and "fedora_abbrev" not in license.keys():
            # entry has an SPDX abbreviation but not a Fedora one
            outdir = os.path.realpath(os.path.join(cwd, "spdx_abbrev"))
            outfile = "%s.yaml" % license["spdx_abbrev"]
        else:
            # entry has no known abbreviation, using full name from JSON file
            outdir = os.path.realpath(os.path.join(cwd, "other"))
            outfile = "%s.yaml" % k

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)

        # strike undesirable characters from the output filename
        outfile = outfile.replace("/", "_").replace(" ", "_").replace("(", "").replace(")", "").replace("!", "").replace("C#", "Csharp").replace("Microsoft's", "Microsoft")

        with open(os.path.join(outdir, outfile), "w") as yamlout:
            yamlout.write("---\n")
            yaml.dump(license, yamlout, default_flow_style=False)
