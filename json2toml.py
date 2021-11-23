#!/usr/bin/python3
#
# Quick and Dirty script to convert license CSV file to individual TOML files.
#
# David Cantrell <dcantrell@redhat.com>
#

import os
import sys
import csv
import textwrap

def usage(cmd):
    print("Usage: %s [tsv file] [output dir]" % os.path.basename(cmd))

def write_bad_row(output, row):
    o = open(output, "a")
    o.write("\t".join(row))
    o.write("\n")
    o.close()

if __name__ == "__main__":
    line = 1

    if len(sys.argv) != 3:
        usage(sys.argv[0])
        sys.exit(1)

    cwd = os.getcwd()
    outdir = sys.argv[2]
    badrows = os.path.join(cwd, "bad.tsv")

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
        #     1 Fedora Short Name
        #     2 SPDX Short Identifier
        #     3 <empty column>
        #     4 On SPDX list?
        #     5 SPDX-Fedora identifiers compare?
        #     6 1:1 replaceable?
        #     7 Notes (2021)
        #     8 Fedora license URL
        #     9 Notes on license (old)

        # The first row are the column headers
        if len(row) >= 2 and row[0] == "Fedora Full Name" and row[1] == "Fedora Short Name":
            line += 1
            continue

        # get the fedora name
        if len(row) >= 1:
            fedora_name = row[0]

        # get the fedora abbreviation
        if len(row) >= 2:
            fedora_abbrev = row[1]

        # collect SPDX expression
        if len(row) >= 3:
            spdx_expression = row[2]

        # collect notes
        if len(row) >= 8 and row[7] != "":
            notes = row[7]
        if len(row) >= 10 and row[9] != "":
            if notes == "":
                notes = row[9]
            else:
                notes += " " + row[9]

        # collect text (url)
        if len(row) >= 9 and row[8] != "":
            text = row[8]

        # process
        if spdx_expression == "":
            print("unable to convert line %d (missing SPDX expression), writing to bad.tsv" % line)
            write_bad_row(badrows, row)
            line += 1
            continue
        elif spdx_expression.find("<") != -1 or spdx_expression.find(">") != -1:
            print("unable to convert line %d (<> found in field), writing to bad.tsv" % line)
            write_bad_row(badrows, row)
            line += 1
            continue
        elif spdx_expression.find("...") != -1:
            print("unable to convert line %d (... found in field), writing to bad.tsv" % line)
            write_bad_row(badrows, row)
            line += 1
            continue

        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)

        output_file = os.path.join(outdir, spdx_expression.replace(" ", "_") + ".toml")

        # write output file
        o = open(output_file, "w")
        o.write("[license]\n\n")
        o.write("expression = \"%s\"\n" % spdx_expression)
        o.write("status = \"approved\"\n")

        if text != "":
            o.write("\ntext = '''\n")
            o.write("\n".join(textwrap.wrap(text, width=80)))
            o.write("\n'''\n")

        if fedora_name != "" or fedora_abbrev != "" or notes != "":
            o.write("\n[fedora]\n\n")

            if fedora_name != "":
                o.write("name = \"%s\"\n" % fedora_name)

            if fedora_abbrev != "":
                o.write("abbreviation = \"%s\"\n" % fedora_abbrev)

            if notes != "":
                if fedora_name != "" or fedora_abbrev != "":
                    o.write("\n")

                o.write("notes = '''\n")
                o.write("\n".join(textwrap.wrap(notes, width=80)))
                o.write("\n'''\n")

        o.close()
        line += 1

    f.close()
