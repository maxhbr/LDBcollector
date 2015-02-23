#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Copyright 2012,2015  Kuno Woudt <kuno@frob.nl>

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


def short_name (li_id, identifier, version, jurisdiction):
    """ Return a short display name, e.g. "Apache-1". """

    if unicode(version) == '4.0':
        return unicode(identifier)

    # This is a quick hack to get a string identical to the value
    # of dc:identifier set by the license_name macro here:
    # http://code.creativecommons.org/viewgit/cc.engine.git/tree/cc/engine/templates/licenses/standard_deed.html#n19

    id = ""
    ver = ""
    jur = ""

    if not identifier:
        print ("WARNING:", li_id, "does not have a dc:identifier")
        return None

    if "mark" == identifier:
        return "Public Domain"

    if ("devnations" in identifier or "sampling" in identifier):
        id = (identifier
            .replace ("nc", "NC")
            .replace ("devnations", "Devnations")
            .replace ("sampling", "Sampling"))
    else:
        id = identifier.upper ()

    if version:
        ver = " " + version

    if jurisdiction:
        j = jurisdiction.replace ("http://creativecommons.org/international/", "")
        jur = " " + j.split ("/")[0].upper ()

    return "CC %s%s%s" % (id, ver, jur)


def parse_rdf (root, identifier, filename):
    contents = ""
    with codecs.open (filename, "rb", "utf-8") as f:
        contents = f.read ()

    # patch some invalid language tags.
    contents = contents.replace('xml:lang="sr@latin"', 'xml:lang="sr"')
    # use "zxx no linguistic content, not applicable" for these template strings.
    contents = contents.replace('xml:lang="i18n"', 'xml:lang="zxx"')

    g = rdflib.Graph ()
    load_namespaces (root, g)
    g.parse (data=contents)

    url = rdflib.term.URIRef('https://licensedb.org/id/' + identifier)
    id = rdflib.term.Literal(identifier)
    g.add((url, LI.id, id));

    return g


def enrich (graph, spdx):
    upstream_url = graph.value (None, a, CC.License)

    (licensedb_url, licensedb_id) = graph[:LI.id:].next()

    graph.add ((licensedb_url, OWL.sameAs, upstream_url))
    graph.add ((upstream_url, OWL.sameAs, licensedb_url))
    graph.add ((licensedb_url, a, LI.License))

    for s, p, o in graph:
        if (p.startswith ("http://purl.org/dc/elements/1.1/")):
            new_p = rdflib.term.URIRef (p.replace ("http://purl.org/dc/elements/1.1/", "http://purl.org/dc/terms/"))
            graph.remove ((s, p, o))
            graph.add ((s, new_p, o))

    for s, p, o in graph:
        if (s == upstream_url
            and o != upstream_url
            and p != OWL.sameAs
            and p != DC.isReplacedBy
            and p != DC.replaces):
            graph.add ((licensedb_url, p, o))

    if licensedb_id in spdx.text:
        graph.add ((licensedb_url, SPDX.licenseId, licensedb_id))
        spdx_url = rdflib.term.URIRef('http://spdx.org/licenses/' + unicode(licensedb_id))
        graph.add ((licensedb_url, SCHEMA.sameAs, spdx_url))

    if licensedb_id.endswith('-4.0'):
        # the 4.0 versions are missing dc:hasVersion
        graph.add ((licensedb_url, DC.hasVersion, rdflib.term.Literal ('4.0')))
        graph.add ((upstream_url, DC.hasVersion, rdflib.term.Literal ('4.0')))

        # the 4.0 versions are missing a logo
        logo = upstream_url.replace('http://creativecommons.org/licenses/',
                                    'http://i.creativecommons.org/l/') + '88x31.png'
        graph.add ((licensedb_url, FOAF.logo, rdflib.term.URIRef(logo)))


    if licensedb_id.endswith('-3.0'):
        # the 3.0 and 4.0 versions don't have isReplacedBy / replaces links
        upstream_ver4 = rdflib.term.URIRef (upstream_url.replace('/3.0/', '/4.0/'))
        graph.add ((upstream_url, DC.isReplacedBy, upstream_ver4))

    plaintext(licensedb_id, licensedb_url, upstream_url, graph)

    cc_dc_id =      graph.value (upstream_url, DC.identifier, None)
    cc_dc_version = graph.value (upstream_url, DC.hasVersion, None)
    cc_jurisdiction = graph.value (upstream_url, CC.jurisdiction, None)

    name = short_name (licensedb_id, cc_dc_id, cc_dc_version, cc_jurisdiction)
    if name:
        graph.add ((licensedb_url, LI.name, rdflib.term.Literal (name)))

    if (unicode(cc_dc_id) in [ "by", "by-sa", "publicdomain" ]
        or " BY " in cc_dc_id or " BY-SA " in cc_dc_id):
        org_cc = rdflib.term.URIRef('http://creativecommons.org/')
        org_fsf = rdflib.term.URIRef('http://fsf.org/')
        org_debian = rdflib.term.URIRef('http://debian.org/')
        org_freedomdefined = rdflib.term.URIRef('http://freedomdefined.org/')

        # http://code.creativecommons.org/viewgit/cc.license.git/tree/cc/license/_lib/classes.py#n127
        # http://freedomdefined.org/Licenses
        # http://www.gnu.org/licenses/license-list.html#ccby
        # http://wiki.debian.org/DFSGLicenses#Creative_Commons_Attribution_Share-Alike_.28CC-BY-SA.29_v3.0

        graph.add((licensedb_url, LI.libre, org_cc))
        if unicode(cc_dc_version) == "2.0" and not cc_jurisdiction:
            graph.add((licensedb_url, LI.libre, org_fsf))

        if unicode(cc_dc_version) == "3.0" and not cc_jurisdiction:
            graph.add((licensedb_url, LI.libre, org_debian))
            graph.add((licensedb_url, LI.libre, org_freedomdefined))

        if unicode(cc_dc_version) == "4.0" and not cc_jurisdiction:
            graph.add((licensedb_url, LI.libre, org_fsf))
            graph.add((licensedb_url, LI.libre, org_debian))
            graph.add((licensedb_url, LI.libre, org_freedomdefined))

    return (licensedb_id, licensedb_url, upstream_url)


def get_rdf_data (root, rdf_path):
    for entry in sorted (os.listdir (rdf_path)):
        if entry.endswith ('.rdf') and entry.startswith ('CC-'):
            identifier = entry.replace ('.rdf', '')
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
        print ("writing    ", turtle_file)
        turtle.write (graph.serialize(format='turtle'))


def main ():
    root = dirname (dirname (dirname (abspath (__file__))))
    rdf_path = join (root, 'upstream', 'rdf')

    spdx_license_list = "http://spdx.org/licenses/"
    spdx = requests.get (spdx_license_list)
    if spdx.status_code != 200:
        print ("Could not load", spdx_license_list)
        sys.exit (1)

    graphs = collections.OrderedDict()
    graphs_by_url = collections.OrderedDict()
    mapping = collections.OrderedDict()

    count = 0
    for graph in get_rdf_data (root, rdf_path):
        identifiers = enrich (graph, spdx)
        (id, url, ccurl) = identifiers
        print ("processing ", id)

        graphs[identifiers] = graph
        graphs_by_url[url] = graph
        mapping[ccurl] = url

    for (identifiers, graph) in graphs.iteritems ():
        (id, url, ccurl) = identifiers
        replacedBy = graph.value (ccurl, DC.isReplacedBy, None)
        if replacedBy in mapping:
            replacement_url = mapping[replacedBy]
            graph.add((url, DC.isReplacedBy, replacement_url))
            graphs_by_url[replacement_url].add ((replacement_url, DC.replaces, url))

    for (identifiers, graph) in graphs.iteritems ():
        (id, url, ccurl) = identifiers
        write_turtle (id, root, graph)

if __name__ == '__main__':
    main ()
