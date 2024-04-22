#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../../upstream/rdf

wget http://www.gnu.org/licenses/gpl-2.0.rdf --output-document $DEST/GPL-2.rdf
wget http://www.gnu.org/licenses/gpl-3.0.rdf --output-document $DEST/GPL-3.rdf
wget http://www.gnu.org/licenses/agpl-3.0.rdf --output-document $DEST/AGPL-3.rdf
wget http://www.gnu.org/licenses/lgpl-2.1.rdf --output-document $DEST/LGPL-2.1.rdf
wget http://www.gnu.org/licenses/lgpl-3.0.rdf --output-document $DEST/LGPL-3.rdf
wget http://www.gnu.org/licenses/fdl-1.3.rdf --output-document $DEST/GFDL-1.3.rdf
