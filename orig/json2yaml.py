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

        license = {"name": k,
                   "approved": entry["approved"],
                   "fedora_abbrev": entry["fedora_abbrev"],
                   "fedora_name": entry["fedora_name"],
                   "id": entry["id"],
                   "license_text": entry["license_text"],
                   "spdx_abbrev": entry["spdx_abbrev"],
                   "spdx_name": entry["spdx_name"],
                   "url": entry["url"]}

        if entry["fedora_abbrev"] != "":
            # entry has a Fedora abbreviation
            outdir = os.path.realpath(os.path.join(cwd, "fedora_abbrev"))
            outfile = "%s.yml" % entry["fedora_abbrev"]
        elif entry["spdx_abbrev"] != "" and entry["fedora_abbrev"] == "":
            # entry has an SPDX abbreviation but not a Fedora one
            outdir = os.path.realpath(os.path.join(cwd, "spdx_abbrev"))
            outfile = "%s.yml" % entry["spdx_abbrev"]
        else:
            # entry has no known abbreviation, using full name from JSON file
            outdir = os.path.realpath(os.path.join(cwd, "other"))
            outfile = "%s.yml" % k

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)

        # in case our outfile name has a slash in it, go with good old
        # first time Linux user "spaces"
        outfile = outfile.replace("/", "_")

        with open(os.path.join(outdir, outfile), "w") as yamlout:
            yamlout.write("---\n")
            yaml.dump(license, yamlout, default_flow_style=False)
