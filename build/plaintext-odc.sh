#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../plaintext

# NOTE: There is no official plain-text version of PDDL 1.0
wget http://www.opendatacommons.org/wp-content/uploads/2009/06/odbl-10.txt --output-document $DEST/ODbL-1.txt
wget http://www.opendatacommons.org/wp-content/uploads/2010/01/odc_by_1.0_public_text.txt --output-document $DEST/ODC-BY-1.txt
wget http://www.opendatacommons.org/wp-content/uploads/2009/06/dbcl-10.txt --output-document $DEST/DbCL-1.txt

