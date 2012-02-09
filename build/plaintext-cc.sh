#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../upstream/plaintext

# NOTE: most creative commons licenses do not have an official plain/text
# version (http://creativecommons.org/weblog/entry/27094).  We're only
# downloading the official plain/text versions.

wget http://creativecommons.org/licenses/by/3.0/legalcode.txt --output-document $DEST/CC-BY-3.txt
wget http://creativecommons.org/licenses/by-sa/3.0/legalcode.txt --output-document $DEST/CC-BY-SA-3.txt
wget http://creativecommons.org/licenses/by-nd/3.0/legalcode.txt --output-document $DEST/CC-BY-ND-3.txt
wget http://creativecommons.org/licenses/by-nc/3.0/legalcode.txt --output-document $DEST/CC-BY-NC-3.txt
wget http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode.txt --output-document $DEST/CC-BY-NC-SA-3.txt
wget http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode.txt --output-document $DEST/CC-BY-NC-ND-3.txt
wget http://creativecommons.org/publicdomain/zero/1.0/legalcode.txt --output-document $DEST/CC0-1.txt
