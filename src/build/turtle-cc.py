#!/usr/bin/python

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

import re
import requests

def get_urls(rdf_path):
    for entry in os.listdir (rdf_path):
        if entry.endswith ('.rdf') and entry.startswith ('CC-'):
            with open (join (rdf_path, entry), "rb") as rdf:
                body = rdf.read ()
                m = re.search ('rdf:about="(.*)"', body)
                yield (entry.replace ('.rdf', ''), m.group (1))

def has_plaintext(ccurl):
    txturl = ccurl + 'legalcode.txt'
    r = requests.head (txturl)
    if r.status_code == 200:
        return txturl

    return False


if __name__ == '__main__':
    root = dirname (dirname (dirname (abspath (__file__))))
    rdf_path = join (root, 'upstream', 'rdf')

    spdx_license_list = "http://spdx.org/licenses/"
    spdx = requests.get (spdx_license_list)
    if spdx.status_code != 200:
        print "Could not load", spdx_license_list
        sys.exit (1)

    for (id, url) in get_urls (rdf_path):
        turtle_file = join (root, "data", id + ".turtle")

        spdxid = ""
        plaintext = ""
        if id in spdx.text:
            spdxid = "   spdx:licenseId \"%s\";\n" % (id)

        txturl = has_plaintext (url)
        if txturl:
            plaintext = "   li:plaintext <%s>;\n" % (txturl)

        with open (turtle_file, "wb") as turtle:
            print "writing", turtle_file
            turtle.write ("""@prefix li: <https://licensedb.org/ns#> .
@prefix spdx: <http://spdx.org/rdf/terms#> .

<%s> a li:License;
%s%s   li:id "%s".
""" % (url, plaintext, spdxid, id))


