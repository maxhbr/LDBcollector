#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

ROOT=$DIR/../..
DEST=$ROOT/upstream/rdf

cd $ROOT
git submodule update --init
mkdir --parents .build

ls upstream/creativecommons/cc/licenserdf/licenses/ > .build/filenames.txt
cat .build/filenames.txt | sed 's/creativecommons.org_licenses_/CC-/' | sed 's/creativecommons.org_publicdomain_/CC-/' | sed 's/_/-/g' | sed 's/-by-/-BY-/' | sed 's/-nc-/-NC-/' | sed 's/-nd-/-ND-/' | sed 's/-sa-/-SA-/' | sed 's/sampling/Sampling/' | sed 's/devnations/Devnations/'  | sed 's/-.rdf/.rdf/' | sed 's/CC-mark-1.0/CC-PD-mark/' | sed 's/CC-zero-1.0/CC0/' > .build/newnames.txt
cat .build/newnames.txt | sed "s,^,$DEST/," > .build/destnames.txt

cd upstream/creativecommons/cc/licenserdf/licenses/
paste $ROOT/.build/filenames.txt $ROOT/.build/destnames.txt | sed 's/^/cp /' | sh

cd $ROOT/upstream/rdf

rm Makefile.am
rm CC-BSD.rdf
rm CC-GPL-2.0.rdf
rm CC-LGPL-2.1.rdf
rm CC-MIT.rdf
rm CC-publicdomain.rdf

