#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../upstream/plaintext

wget http://www.apache.org/licenses/LICENSE-2.0.txt --output-document $DEST/Apache-2.txt
wget http://www.apache.org/licenses/LICENSE-1.1 --output-document $DEST/Apache-1.1.txt
wget http://www.apache.org/licenses/LICENSE-1.0 --output-document $DEST/Apache-1.txt
wget http://unlicense.org/UNLICENSE --output-document $DEST/unlicense.txt
wget http://git.savannah.gnu.org/cgit/threadmill.git/plain/COPYING.WTFPL --output-document $DEST/WTFPL-1.1.txt
wget http://sam.zoy.org/wtfpl/COPYING --output-document $DEST/WTFPL-2.txt
wget http://www.ncftp.com/ncftp/doc/LICENSE.txt --output-document $DEST/Clarified-Artistic.txt
