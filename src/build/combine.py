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
import datetime
from os.path import abspath, dirname, isfile, join
from misc import activate_virtualenv

activate_virtualenv ('licensedb')

import codecs
import json
import rdflib

from sre_compile import isstring

def load_namespaces (root, graph):
    with open (join (root, 'data', 'context.jsonld'), "rb") as f:
        context = json.loads (f.read ())

        for prefix, url in context["@context"].items ():
            if isstring (url):
                graph.namespace_manager.bind (prefix, url)


def parse_rdf (root, graph, filename):
    contents = ""
    with codecs.open (filename, "rb", "utf-8") as f:
        contents = f.read ()

    print ("processing ", filename.replace(root + '/', ''))
    graph.parse (data=contents, format='turtle')



def main ():
    root = dirname (dirname (dirname (abspath (__file__))))
    data_path = join (root, 'www', 'id')

    g = rdflib.Graph ()
    load_namespaces (root, g)

    for entry in sorted (os.listdir (data_path)):
        if entry.endswith ('.ttl'):
            parse_rdf (root, g, join (data_path, entry))

    dst_filename = join (root, 'www', 'dl', 'licensedb.ttl')

    with open (dst_filename, "wb") as turtle:
        print ("writing    ", dst_filename.replace (root + '/', ''))
        turtle.write (g.serialize(format='turtle'))


if __name__ == '__main__':
    main ()
