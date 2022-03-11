#!/usr/bin/python3
#
# Quick and Dirty script to convert license CSV file to individual TOML files.
# And by CSV, I mean TSV because CSV from Google's spreadsheet is unusual and
# TSV is more reliable.
#
# David Cantrell <dcantrell@redhat.com>
#

import os
import sys
import csv
import textwrap

def usage(cmd):
    print("Usage: %s [tsv file] [output dir]" % os.path.basename(cmd))

def write_licenses(outdir, licenses):
    if not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)

    for license in licenses.keys():
        entry = licenses[license]
        output_file = os.path.join(outdir, license.strip().replace(" ", "_").replace("/", "-") + ".toml")

        # write output file
        o = open(output_file, "w")
        o.write("[license]\n\n")
        o.write("expression = [ \"%s\" ]\n" % entry["spdx_expression"].strip())
        o.write("status = \"not approved\"\n")

        if entry["text"] != "":
            entry["text"] = entry["text"].strip()
            o.write("\ntext = '''\n")
            o.write("\n".join(textwrap.wrap(entry["text"], width=80)))
            o.write("\n'''\n")

        if "fedora_names" in entry.keys() or "fedora_abbrev" in entry.keys() or "fedora_notes" in entry.keys():
            o.write("\n[fedora]\n\n")
            have = False

            if "fedora_names" in entry.keys() and entry["fedora_names"] != []:
                o.write("name = [\n")
                i = 1

                for name in entry["fedora_names"]:
                    o.write("    \"%s\"" % name)

                    if i < len(entry["fedora_names"]):
                        o.write(",\n")

                    i += 1

                o.write("\n]\n")
                have = True

            if "fedora_abbrev" in entry.keys() and entry["fedora_abbrev"] != []:
                if have:
                    o.write("\n")

                o.write("abbreviation = [\n")
                i = 1

                for abbrev in entry["fedora_abbrev"]:
                    o.write("    \"%s\"" % abbrev)

                    if i < len(entry["fedora_abbrev"]):
                        o.write(",\n")

                    i += 1

                o.write("\n]\n")
                have = True

            if "fedora_notes" in entry.keys() and entry["fedora_notes"] != "":
                if have:
                    o.write("\n")

                o.write("notes = '''\n")
                o.write("\n".join(textwrap.wrap(entry["fedora_notes"], width=80)))
                o.write("\n'''\n")

        o.close()

def write_bad_row(output, row):
    o = open(output, "a")
    o.write("\t".join(row))
    o.write("\n")
    o.close()

if __name__ == "__main__":
    line = 1
    licenses = {}

    if len(sys.argv) != 3:
        usage(sys.argv[0])
        sys.exit(1)

    cwd = os.getcwd()
    outdir = sys.argv[2]
    badrows = os.path.join(cwd, "errors.tsv")

    f = open(os.path.realpath(sys.argv[1]), newline='')
    csvdata = csv.reader(f, delimiter='\t')

    for row in csvdata:
        fedora_name = ""
        fedora_abbrev = ""
        spdx_expression = ""
        notes = ""
        text = ""

        if "".join(row) == "":
            line += 1
            continue

        # we are done with this condition
        if len(row) >= 1 and row[0].find("listed licenses on Fedora good list") != -1:
            break

        # columns are:
        #     0 Fedora Full Name
        #     1 SPDX Short Identifier
        #     2 Upstream URL
        #     3 Fedora Notes
        #     4 Other Notes

        # get the fedora name
        if len(row) >= 1:
            fedora_name = row[0]

        # collect SPDX expression
        if len(row) >= 2 and row[1] != "":
            spdx_expression = row[1]

        # collect text (url)
        if len(row) >= 3 and row[2] != "":
            text = row[2]

        # collect notes
        if len(row) >= 4 and row[3] != "":
            notes = row[3]
        if len(row) >= 5 and row[4] != "":
            if notes == "":
                notes = row[4]
            else:
                notes += "\n\n" + row[4]

        # process
        if spdx_expression.find("<") != -1 or spdx_expression.find(">") != -1:
            print("unable to convert line %d (<> found in field), writing to errors.tsv" % line)
            write_bad_row(badrows, row)
            line += 1
            continue
        elif spdx_expression.find("...") != -1:
            print("unable to convert line %d (... found in field), writing to errors.tsv" % line)
            write_bad_row(badrows, row)
            line += 1
            continue

        # add to the licenses hash
        entry = licenses.get(fedora_name)

        if entry is None:
            # new license entry
            new_entry = {}
            new_entry["spdx_expression"] = spdx_expression
            new_entry["text"] = text
            new_entry["fedora_names"] = [fedora_name]
            new_entry["fedora_abbrev"] = [fedora_abbrev]
            new_entry["fedora_notes"] = notes
            licenses[fedora_name] = new_entry
        else:
            # existing entry, add the fedora data
            if fedora_name not in entry["fedora_names"]:
                entry["fedora_names"].append(fedora_name)

            if fedora_abbrev not in entry["fedora_abbrev"]:
                entry["fedora_abbrev"].append(fedora_abbrev)

            if text != "":
                entry["text"] += "\n\n" + text

            if notes != "":
                entry["fedora_notes"] += "\n\n" + notes

        line += 1

    f.close()

    # write the results
    write_licenses(outdir, licenses)
