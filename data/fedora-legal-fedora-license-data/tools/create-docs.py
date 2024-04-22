#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:

# Copyright Fedora License Data Project Authors.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import jinja2
import json
import os
import sys
import tomllib

parser = argparse.ArgumentParser(description='Converts license data file to AsciiDoc page with overview of all licenses')
parser.add_argument('datadir', help='path to directory with TOML files', default="data/")
parser.add_argument('--verbose', '-v', action='count', default=0)
opts = parser.parse_args()

TEMPLATES = ["templates/allowed-licenses.adoc.j2", "templates/not-allowed-licenses.adoc.j2", "templates/all-allowed.adoc.j2"]
#"license-overview-template.jinja2"

# function used in Jinja template
def spdx_url(license):
    """ Returns url to SPDX license """
    spd_expression = license['license']['expression']
    if spd_expression.startswith("LicenseRef-"):
        return 'link:++https://gitlab.com/fedora/legal/fedora-license-data/-/blob/main/data/{0}.toml++[{0}] link:++https://docs.fedoraproject.org/en-US/legal/license-review-process/#_what_is_licenseref++[icon:info-circle[]]'.format(spd_expression)
    if "WITH" in spd_expression:
        expanded_list = spd_expression.split("WITH")
        return "link:++https://spdx.org/licenses/{0}.html++[{0}] WITH link:++https://spdx.org/licenses/{1}.html++[{1}]".format(expanded_list[0].strip(), expanded_list[1].strip())
#    if 'url' in license['license']:
#        return license['license']['url'].strip()
    return "link:++https://spdx.org/licenses/{0}.html++[{0}]".format(spd_expression)

def additional_urls(license):
    """ returns additional urls if present, in html form """
    if 'url' in license['license']:
        RESULT = []
        for url in license['license']['url'].split():
            RESULT.append('link:++{0}++[]'.format(url))
        return ' '.join(RESULT)
    return ''


func_dict = {
    "spdx_url": spdx_url,
    "additional_urls": additional_urls,
}


ALL_ALLOWED_LICENSES = []
ALLOWED_LICENSES = []
CONTENT_LICENSES = []
DOCUMENTATION_LICENSES = []
FONTS_LICENSES = []
FIRMWARE_LICENSES = []
NOTALLOWED_LICENSES = []

for licensefile in os.scandir(opts.datadir):
    # all license data files must be *.toml files
    if not licensefile.name.endswith(".toml"):
        continue

    # read in the data file
    with open(licensefile.path, 'rb') as f:
        data = tomllib.load(f)
    # {'license': {'expression': 'OpenSSL', 'status': ['allowed'], 'url': 'http://www.sdisw.com/openssl.htm\n'}, 'fedora': {'legacy-name': ['OpenSSL License'], 'legacy-abbreviation': ['OpenSSL']}}

    if 'allowed' in data["license"]["status"]:
        ALLOWED_LICENSES.append(data)
    if 'allowed-content' in data["license"]["status"]:
        CONTENT_LICENSES.append(data)
    if 'allowed-documentation' in data["license"]["status"]:
        DOCUMENTATION_LICENSES.append(data)
    if 'allowed-fonts' in data["license"]["status"]:
        FONTS_LICENSES.append(data)
    if 'allowed-firmware' in data["license"]["status"]:
        FIRMWARE_LICENSES.append(data)
    if 'not-allowed' in data["license"]["status"]:
        NOTALLOWED_LICENSES.append(data)
    else:
        ALL_ALLOWED_LICENSES.append(data)


for template_filename in TEMPLATES:
    filename = os.path.join(os.path.dirname(__file__), template_filename)
    with open(filename) as f:
        template = jinja2.Template(f.read())
    template.globals.update(func_dict)
    msg = template.render(ALLOWED_LICENSES=ALLOWED_LICENSES,
                          CONTENT_LICENSES=CONTENT_LICENSES,
                          DOCUMENTATION_LICENSES=DOCUMENTATION_LICENSES,
                          FONTS_LICENSES=FONTS_LICENSES,
                          FIRMWARE_LICENSES=FIRMWARE_LICENSES,
                          NOTALLOWED_LICENSES=NOTALLOWED_LICENSES,
                          ALL_ALLOWED_LICENSES=ALL_ALLOWED_LICENSES)
    new_filename = os.path.splitext(os.path.basename(template_filename))[0]
    file = open(new_filename, "w")
    file.write(msg)
    file.close()
