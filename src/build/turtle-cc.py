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
from os.path import abspath, dirname, isfile, join

def activate_virtualenv (appname):
    """ This will look for an application specific virtualenv in
    $XDG_DATA_HOME/<appname>/virtualenv and activate it if present. """

    data_home = os.getenv ('XDG_DATA_HOME')
    if not data_home:
        home = os.getenv ('HOME')
        if not home:
            print ('ERROR: $HOME environment variable not set')
            sys.exit (1)

        data_home = join (home, '.local', 'share')

    ve_activate = join (data_home, appname, 'virtualenv', 'bin', 'activate_this.py')

    if isfile (ve_activate):
        execfile (ve_activate, dict (__file__ = ve_activate))

activate_virtualenv ('licensedb')

import collections
import re
import requests
import rdflib
import rdflib.term


class License (object):
    id = None
    uri = None
    replacedBy = None
    earlierVersion = None
    laterVersion = None

    def __init__ (self, identifier = None):
        self.id = identifier

    def __str__ (self):
        return (", ".join (filter (lambda x: x, [
                        self.id, self.uri, self.replacedBy,
                        self.earlierVersion, self.laterVersion])))


def parse_rdf (license_, filename):
    g = rdflib.Graph ()
    g.load (filename)

    rdf_type = rdflib.term.URIRef ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    cc_license = rdflib.term.URIRef ("http://creativecommons.org/ns#License")
    replaced_by = rdflib.term.URIRef ("http://purl.org/dc/terms/isReplacedBy")

    for s, p, o in g:
        if p == rdf_type and o == cc_license:
            license_.uri = unicode (s)

        if p == replaced_by:
            license_.replacedBy = unicode (o)

    return license_


def get_rdf_data (rdf_path):
    for entry in os.listdir (rdf_path):
        if entry.endswith ('.rdf') and entry.startswith ('CC-'):
            license_ = License (entry.replace ('.rdf', ''))
            yield parse_rdf (license_, join (rdf_path, entry))


def has_plaintext(ccurl):
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

    if rdf.id in spdx.text:
        spdxid = "   spdx:licenseId \"%s\";\n" % (rdf.id)

    txturl = has_plaintext (rdf.uri)
    if txturl:
        plaintext = "   li:plaintext <%s>;\n" % (txturl)

    if rdf.earlierVersion:
        earlierVersion = "   li:earlierVersion <%s>;\n" % (rdf.earlierVersion)

    if rdf.laterVersion:
        laterVersion = "   li:laterVersion <%s>;\n" % (rdf.laterVersion)

    with open (turtle_file, "wb") as turtle:
        print ("writing", turtle_file)
        turtle.write ("""@prefix li: <https://licensedb.org/ns#> .
@prefix spdx: <http://spdx.org/rdf/terms#> .

<%s> a li:License;
%s%s%s%s   li:id "%s".
""" % (rdf.uri, plaintext, earlierVersion, laterVersion, spdxid, rdf.id))


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
