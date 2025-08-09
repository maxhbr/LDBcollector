#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# Looks for unknown licenses in a file with license (expressions)
#     check-license-file.sh <LICENSE-FILE>
# 

SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})/../
cat $1 | while read LICENSE
do
    COMMENT=$(echo $LICENSE | grep -c "^#")
    if [ $COMMENT -ne 0 ]
    then
        echo "ignore comment: $LICENSE" 1>&2
        continue
    fi
    printf "unknown\n$LICENSE\n" 
done | ${SCRIPT_DIR}/devel/flame shell -s | grep -v Unknown
