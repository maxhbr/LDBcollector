#!/bin/bash

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

RET=0

CONF_VERSION=$(grep SW_VERSION python/flame/config.py | sed 's,[ ]*",,g' | cut -d = -f 2)
MD_VERSION=$(grep "^#" VERSION.md | head -1 | sed 's,^# ,,g')
FLAME_VERSION=$(PYTHONPATH=./python ./python/flame/__main__.py --version)

#echo "\"$CONF_VERSION\" \"$MD_VERSION\" \"$FLAME_VERSION\""

echo -n "Check version information: "
if [ "$CONF_VERSION" = "$MD_VERSION" ] && [ "$MD_VERSION" = "$FLAME_VERSION" ]
then
    echo "OK"
else
    echo "Failed"
    RET=1
fi

GIT_TAG_PRESENT=$(git tag | grep -c "$MD_VERSION")
echo -n "Check git tag: "
if [ $GIT_TAG_PRESENT -ne 0 ]
then
    echo "OK"
else
    echo "Warning"
fi

exit $RET
        
