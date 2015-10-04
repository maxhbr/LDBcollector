
LicenseDB
=========

This repository contains the LicenseDB project website and database. Please see
https://licensedb.org/ for more information.

See LICENSE.txt for license information.


Build
=====

To generate the HDT dump RDFHDT needs to be installed, download that from
http://www.rdfhdt.org/download/

For some RDF conversions the "rapper" tool from raptor2-utils is required:

    sudo apt-get install raptor2-utils

To build and run the software you also need python 2.7 and a recent version of
io.js or node.js.  Download io.js from https://iojs.org/en/

    sudo apt-get install python-virtualenv python-pip
    bin/bootstrap.sh
    scons

