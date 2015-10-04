#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../../upstream/plaintext

curl http://www.affero.org/source/latest.tar.gz | gunzip | tar xv ./svcs/doc/COPYING
cat svcs/doc/COPYING | recode latin1..utf8 > $DEST/AGPL-1.txt

