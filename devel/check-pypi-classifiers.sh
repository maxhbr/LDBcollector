#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Script to check if all python classifiers as listed over at
# https://pypi.org/pypi?%3Aaction=list_classifiers, with some
# exceptions, are managed

# default exit code
EXIT_CODE=0


CLASSIFIERS_FILE=classifiers.txt

# List of licenses not yet supported
NOT_HANDLED=" \
              -e 'License :: Aladdin Free Public License (AFPL)' \
              -e 'License :: DFSG approved' \
              -e 'License :: Free For Educational Use'  \
              -e 'License :: Free For Home Use'  \
              -e 'License :: Free To Use But Restricted'  \
              -e 'License :: Free for non-commercial use'  \
              -e 'License :: Freely Distributable'  \
              -e 'License :: Freeware'  \
              -e 'License :: GUST Font License 1.0'  \
              -e 'License :: GUST Font License 2006-09-30'  \
              -e 'License :: Other/Proprietary License'  \
              -e 'License :: OSI Approved :: Qt Public License (QPL)'
              "


# Download all classifiers
if [ ! -f  $CLASSIFIERS_FILE.tmp ]
then
    curl -LJ -o $CLASSIFIERS_FILE.tmp "https://pypi.org/pypi?%3Aaction=list_classifiers"
fi



# Extract licenses that are (or should be) managed
echo "cat $CLASSIFIERS_FILE.tmp | grep ^License  | grep -v $NOT_HANDLED" | bash > $CLASSIFIERS_FILE

handle_license()
{
    local LICENSE="$1"
    echo -n "$LICENSE: "
    PYTHONPATH=./python python3 ./python/flame/__main__.py unknown "$LICENSE" > /dev/null 2>&1
    RET=$?
    if [ $RET -eq 0 ]
    then
        echo "OK"
    else
        EXIT_CODE=$(( $EXIT_CODE + 1 ))
        echo "Failed    $EXIT_CODE"
    fi

}


# Loop through all classifiers in the file
while read CLASSIFIER
do
    handle_license "$CLASSIFIER"
    #sleep 1
done < $CLASSIFIERS_FILE

echo $EXIT_CODE
exit $EXIT_CODE

