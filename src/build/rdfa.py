#!/usr/bin/env python

# Copyright (C) 2013  Kuno Woudt <kuno@frob.nl>

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

import codecs
import rdflib

def parse (filename, uri):
    g = rdflib.Graph ()
    g.parse (uri)
    output = g.serialize (format='xml')
    with codecs.open (filename, "wb", "utf-8") as f:
        f.write (output)

parse ('CC-BY-4.0.rdf', 'http://creativecommons.org/licenses/by/4.0/')
parse ('CC-BY-SA-4.0.rdf', 'http://creativecommons.org/licenses/by-sa/4.0/')
parse ('CC-BY-NC-4.0.rdf', 'http://creativecommons.org/licenses/by-nc/4.0/')
parse ('CC-BY-NC-ND-4.0.rdf', 'http://creativecommons.org/licenses/by-nc-nd/4.0/')
parse ('CC-BY-NC-SA-4.0.rdf', 'http://creativecommons.org/licenses/by-nc-sa/4.0/')
parse ('CC-BY-ND-4.0.rdf', 'http://creativecommons.org/licenses/by-nd/4.0/')



