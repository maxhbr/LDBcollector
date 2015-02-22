#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Copyright 2015  Kuno Woudt <kuno@frob.nl>

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

import codecs
import collections
import json
import re
import requests
import rdflib
import rdflib.term

from rdflib.namespace import RDF
from sre_compile import isstring

a = RDF.type

CC = rdflib.Namespace ('http://creativecommons.org/ns#')
DC = rdflib.Namespace ('http://purl.org/dc/terms/')
FOAF = rdflib.Namespace ('http://xmlns.com/foaf/0.1/')
LI = rdflib.Namespace ('https://licensedb.org/ns#')
OWL = rdflib.Namespace ('http://www.w3.org/2002/07/owl#')
SCHEMA = rdflib.Namespace ('http://schema.org/')
SPDX = rdflib.Namespace ('http://spdx.org/rdf/terms#')

def load_namespaces (root, graph):
    with open (join (root, 'data', 'context.json'), "rb") as f:
        context = json.loads (f.read ())

        for prefix, url in context["@context"].items ():
            if isstring (url):
                graph.namespace_manager.bind (prefix, url)


def parse_rdf (root, identifier, filename):
    contents = ""
    with codecs.open (filename, "rb", "utf-8") as f:
        contents = f.read ()

    g = rdflib.Graph ()
    load_namespaces (root, g)
    print ("processing", filename)
    g.parse (data=contents, format='turtle')

    url = rdflib.term.URIRef('https://licensedb.org/id/' + identifier)
    id = rdflib.term.Literal(identifier)
    g.add((url, LI.id, id));

    return g


def process (root, graph):
    (licensedb_url, licensedb_id) = graph[:LI.id:].next()

    for identifier in graph[licensedb_url:SPDX.licenseId:]:

        # FIXME: sameAs is perhaps too strong for these relationships
        # because LicenseDB doesn't distinguish between different uses of
        # some licenses (e.g. SPDX distinguishes between GPLv3-only and GPLv3-or-later
        # and GPLv3 with various exceptions)

        spdx_url = rdflib.term.URIRef('http://spdx.org/licenses/' + unicode(identifier))
        graph.add ((licensedb_url, SCHEMA.sameAs, spdx_url))

    plaintext_path = join(root, 'www', 'id', licensedb_id + '.txt')
    if isfile(plaintext_path):
        plaintext_url = rdflib.term.URIRef(licensedb_url + '.txt')
        graph.add ((licensedb_url, LI.plaintext, plaintext_url))

    return (licensedb_url, licensedb_id)


def get_rdf_data (root, rdf_path):
    for entry in sorted (os.listdir (rdf_path)):
        if entry.endswith ('.ttl'):
            identifier = entry.replace ('.ttl', '')
            yield parse_rdf (root, identifier, join (rdf_path, entry))


def plaintext(id, url, ccurl, graph):
    has_plaintext = [
        "CC-BY-NC-ND-3.0",
        "CC-BY-NC-SA-3.0",
        "CC-BY-NC-3.0",
        "CC-BY-ND-3.0",
        "CC-BY-SA-3.0",
        "CC-BY-3.0",
        "CC0",
        "CC-BY-NC-ND-4.0",
        "CC-BY-NC-SA-4.0",
        "CC-BY-NC-4.0",
        "CC-BY-ND-4.0",
        "CC-BY-SA-4.0",
        "CC-BY-4.0",
    ]

    if unicode(id) in has_plaintext:
        graph.add ((url, LI.plaintext, ccurl + 'legalcode.txt'))
        graph.add ((url, LI.plaintext, url + '.txt'))


def write_turtle (id, root, graph):
    turtle_file = join (root, "www", "id", id + ".ttl")

    with open (turtle_file, "wb") as turtle:
        print ("writing   ", turtle_file)
        turtle.write (graph.serialize(format='turtle'))


def main ():
    root = dirname (dirname (dirname (abspath (__file__))))
    rdf_path = join (root, 'data')

    for graph in get_rdf_data (root, rdf_path):
        (url, id) = process (root, graph)
        write_turtle (id, root, graph)


if __name__ == '__main__':
    main ()
