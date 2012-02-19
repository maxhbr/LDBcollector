#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../../upstream/plaintext

wget http://www.gnu.org/licenses/gpl-1.0.txt --output-document $DEST/GPL-1.txt
wget http://www.gnu.org/licenses/gpl-2.0.txt --output-document $DEST/GPL-2.txt
wget http://www.gnu.org/licenses/gpl-3.0.txt --output-document $DEST/GPL-3.txt
wget http://www.gnu.org/licenses/agpl-3.0.txt --output-document $DEST/AGPL-3.txt
wget http://www.gnu.org/licenses/lgpl-2.0.txt --output-document $DEST/LGPL-2.txt
wget http://www.gnu.org/licenses/lgpl-2.1.txt --output-document $DEST/LGPL-2.1.txt
wget http://www.gnu.org/licenses/lgpl-3.0.txt --output-document $DEST/LGPL-3.txt
wget http://www.gnu.org/licenses/fdl-1.1.txt --output-document $DEST/GFDL-1.1.txt
wget http://www.gnu.org/licenses/fdl-1.2.txt --output-document $DEST/GFDL-1.2.txt
wget http://www.gnu.org/licenses/fdl-1.3.txt --output-document $DEST/GFDL-1.3.txt
