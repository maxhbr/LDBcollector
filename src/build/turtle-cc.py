#!/usr/bin/python

# Copyright 2012  Kuno Woudt

# All software related to the License Database project is licensed under
# the Apache License, Version 2.0. See the file Apache-2.0.txt for more
# information.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import license
from os.path import abspath, dirname, isfile, join
from license import activate_virtualenv, License

activate_virtualenv ('licensedb')

import collections
import re
import requests
import rdflib
import rdflib.term

def parse_rdf (license_, filename):
    g = rdflib.Graph ()
    g.load (filename)

    rdf_type = rdflib.term.URIRef ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    cc_license = rdflib.term.URIRef ("http://creativecommons.org/ns#License")
    replaced_by = rdflib.term.URIRef ("http://purl.org/dc/terms/isReplacedBy")
    jurisdiction = rdflib.term.URIRef ("http://creativecommons.org/ns#jurisdiction")
    hasVersion1 = rdflib.term.URIRef ("http://purl.org/dc/terms/hasVersion")
    hasVersion2 = rdflib.term.URIRef ("http://purl.org/dc/elements/1.1/hasVersion")
    dcidentifier1 = rdflib.term.URIRef ("http://purl.org/dc/terms/identifier")
    dcidentifier2 = rdflib.term.URIRef ("http://purl.org/dc/elements/1.1/identifier")

    for s, p, o in g:
        if p == rdf_type and o == cc_license:
            license_.uri = unicode (s)

        if p == replaced_by:
            license_.replacedBy = unicode (o)

        if p in [hasVersion1, hasVersion2]:
            license_.hasVersion = unicode (o)

        if p == jurisdiction:
            license_.jurisdiction = unicode (o)

        if p in [dcidentifier1, dcidentifier2]:
            license_.dcidentifier = unicode (o)


    return license_


def get_rdf_data (rdf_path):
    for entry in os.listdir (rdf_path):
        if entry.endswith ('.rdf') and entry.startswith ('CC-'):
            license_ = License (entry.replace ('.rdf', ''))
            yield parse_rdf (license_, join (rdf_path, entry))


def has_plaintext(license):

    # We know only the unported 3.0 licenses currently have a plaintext
    # version.  So only try to get plaintext for 3.0 licenses and newer,
    # and for 3.0 only do so for unported licenses.
    if license.hasVersion in [ "1.0", "1.3", "2.0", "2.1", "2.5" ]:
        return False
    if license.hasVersion in [ "3.0" ] and license.jurisdiction:
        return False

    ccurl = license.uri
    txturl = ccurl + 'legalcode.txt'
    r = requests.head (txturl)
    if r.status_code == 200:
        return txturl

    return False


def write_turtle (spdx, root, rdf):
    turtle_file = join (root, "data", rdf.id + ".turtle")

    spdxid = ""
    plaintext = ""
    earlierVersion = ""
    laterVersion = ""
    name = ""
    libre = ""

    if rdf.id in spdx.text:
        spdxid = "   spdx:licenseId \"%s\";\n" % (rdf.id)

    txturl = has_plaintext (rdf)
    if txturl:
        plaintext = "   li:plaintext <%s>;\n" % (txturl)

    if rdf.earlierVersion:
        earlierVersion = "   dc:replaces <%s>;\n" % (rdf.earlierVersion)

    if rdf.laterVersion:
        laterVersion = "   dc:isReplacedBy <%s>;\n" % (rdf.laterVersion)

    shortname = rdf.short_name ()
    if shortname:
        name = "   li:name \"%s\";\n" % (shortname)

    # http://code.creativecommons.org/viewgit/cc.license.git/tree/cc/license/_lib/classes.py#n127
    # http://freedomdefined.org/Licenses
    # http://www.gnu.org/licenses/license-list.html#ccby
    # http://wiki.debian.org/DFSGLicenses#Creative_Commons_Attribution_Share-Alike_.28CC-BY-SA.29_v3.0
    if rdf.dcidentifier in [ "by", "by-sa", "publicdomain" ]:
        libre = libre + "   li:libre <http://creativecommons.org/>;\n"
        libre = libre + "   li:libre <http://freedomdefined.org/>;\n"
        if rdf.hasVersion == "2.0" and not rdf.jurisdiction:
            libre = libre + "   li:libre <http://fsf.org/>;\n"
        if rdf.hasVersion == "3.0" and not rdf.jurisdiction:
            libre = libre + "   li:libre <http://debian.org/>;\n"

    with open (turtle_file, "wb") as turtle:
        print ("writing", turtle_file)
        turtle.write ("""@prefix li: <https://licensedb.org/ns#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix spdx: <http://spdx.org/rdf/terms#> .

<%s> a li:License;
%s%s%s%s%s%s   li:id "%s".
""" % (rdf.uri, name, plaintext, libre,
       earlierVersion, laterVersion, spdxid, rdf.id))


def main ():
    root = dirname (dirname (dirname (abspath (__file__))))
    rdf_path = join (root, 'upstream', 'rdf')

    spdx_license_list = "http://spdx.org/licenses/"
    spdx = requests.get (spdx_license_list)
    if spdx.status_code != 200:
        print ("Could not load", spdx_license_list)
        sys.exit (1)

    mapping = {}
    earlierVersion = {}

    count = 0
    for rdf in get_rdf_data (rdf_path):
        mapping[rdf.uri] = rdf

    for rdf in mapping.itervalues ():
        if rdf.replacedBy:
            try:
                rdf.laterVersion = 'https://licensedb.org/id/' + mapping[rdf.replacedBy].id
                mapping[rdf.replacedBy].earlierVersion = 'https://licensedb.org/id/' + rdf.id
            except KeyError:
                print ("WARNING: replacedBy refers to non-existent", rdf.replacedBy)


    for rdf in mapping.itervalues ():
        write_turtle (spdx, root, rdf)


if __name__ == '__main__':
    main ()
