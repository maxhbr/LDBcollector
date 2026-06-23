#!/bin/env python3

# SPDX-FileCopyrightText: 2026 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# Adds meta information to a JSON file, used in combo with the
# corresponding shell script
#

import glob
import json
import sys


def _add_data(meta, key, value, forced=False):
    if (key not in meta) or forced:
        meta[key] = value

def add_to_file(filename):
    with open(filename) as fp:
        json_data = json.load(fp)
        fp.close()
        meta = json_data['meta']
        _add_data(meta, 'license', 'CC-BY-4.0')
        _add_data(meta, 'copyright', 'Copyright (c) 2026 Henrik Sandklef <hesa@sandklef.com>')
        _add_data(meta, 'project', 'FOSS Licenses')
        _add_data(meta, 'project_url', 'https://github.com/hesa/foss-licenses/')
        #print(json.dumps(json_data, indent=4))

        with open(filename, "w") as fp:
            json.dump(json_data, fp, indent=4)
            fp.close()


add_to_file(sys.argv[1])
