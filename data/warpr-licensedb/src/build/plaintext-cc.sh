#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../../upstream/plaintext

# NOTE: most creative commons licenses do not have an official plain/text
# version (http://creativecommons.org/weblog/entry/27094).  We're only
# downloading the official plain/text versions.

wget http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode.txt --output-document $DEST/CC-BY-NC-ND-3.0.txt
wget http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode.txt --output-document $DEST/CC-BY-NC-SA-3.0.txt
wget http://creativecommons.org/licenses/by-nc/3.0/legalcode.txt    --output-document $DEST/CC-BY-NC-3.0.txt
wget http://creativecommons.org/licenses/by-nd/3.0/legalcode.txt    --output-document $DEST/CC-BY-ND-3.0.txt
wget http://creativecommons.org/licenses/by-sa/3.0/legalcode.txt    --output-document $DEST/CC-BY-SA-3.0.txt
wget http://creativecommons.org/licenses/by/3.0/legalcode.txt       --output-document $DEST/CC-BY-3.0.txt
wget http://creativecommons.org/publicdomain/zero/1.0/legalcode.txt --output-document $DEST/CC0.txt

wget http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt --output-document $DEST/CC-BY-NC-ND-4.0.txt
wget http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt --output-document $DEST/CC-BY-NC-SA-4.0.txt
wget http://creativecommons.org/licenses/by-nc/4.0/legalcode.txt    --output-document $DEST/CC-BY-NC-4.0.txt
wget http://creativecommons.org/licenses/by-nd/4.0/legalcode.txt    --output-document $DEST/CC-BY-ND-4.0.txt
wget http://creativecommons.org/licenses/by-sa/4.0/legalcode.txt    --output-document $DEST/CC-BY-SA-4.0.txt
wget http://creativecommons.org/licenses/by/4.0/legalcode.txt       --output-document $DEST/CC-BY-4.0.txt

