#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

DEST=$DIR/../../upstream/rdf

mkdir --parents $DIR/.build
cd $DIR/.build
svn co http://code.creativecommons.org/svnroot/license.rdf/trunk/license_rdf/

cd license_rdf
rm creativecommons.org_licenses_GPL_2.0_.rdf
rm creativecommons.org_licenses_LGPL_2.1_.rdf
rm creativecommons.org_licenses_publicdomain_.rdf
rm creativecommons.org_publicdomain_zero_1.0_.rdf
rm Makefile.am

ls > ../filenames.txt
cat ../filenames.txt | sed 's/creativecommons.org_licenses_/CC-/' | sed 's/_/-/g' | sed 's/-by-/-BY-/' | sed 's/-nc-/-NC-/' | sed 's/-nd-/-ND-/' | sed 's/-sa-/-SA-/' | sed 's/sampling/Sampling/' | sed 's/devnations/Devnations/'  | sed 's/-.rdf/.rdf/' > ../newnames.txt

paste ../filenames.txt ../newnames.txt | sed 's/^/mv /' | sh

# for some reason the svn version is missing all dc:titles,
# I hope this isn't true for all the other CC licenses as well.
wget http://creativecommons.org/publicdomain/zero/1.0/rdf --output-document CC0.rdf

# Another document where the online rdf version is different from the
# version in subversion.
wget http://creativecommons.org/licenses/by-nc-nd/2.0/jp/rdf --output-document CC-BY-NC-ND-2.0-jp.rdf

mv *.rdf $DEST

