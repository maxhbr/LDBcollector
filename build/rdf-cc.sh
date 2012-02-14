#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../upstream/rdf

mkdir --parents $DIR/.build
cd $DIR/.build
svn co http://code.creativecommons.org/svnroot/license.rdf/trunk/license_rdf/

cd license_rdf
rm creativecommons.org_licenses_GPL_2.0_.rdf
rm creativecommons.org_licenses_LGPL_2.1_.rdf
rm creativecommons.org_licenses_publicdomain_.rdf
rm Makefile.am

ls > ../filenames.txt
cat ../filenames.txt | sed 's/creativecommons.org_licenses_/CC-/' | sed 's/_/-/g' | sed 's/-by-/-BY-/' | sed 's/-nc-/-NC-/' | sed 's/-nd-/-ND-/' | sed 's/-sa-/-SA-/' | sed 's/sampling/Sampling/' | sed 's/devnations/Devnations/'  | sed 's/-.rdf/.rdf/' > ../newnames.txt

paste ../filenames.txt ../newnames.txt | sed 's/^/mv /' | sh
mv creativecommons.org-publicdomain-zero-1.0.rdf CC0.rdf
mv *.rdf $DEST


