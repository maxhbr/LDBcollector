#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

COL_SIZE=60

bulk_check_singles()
{
    LICENSE="$1"
    EXPECTED="$2"

    printf "%-${COL_SIZE}s" "Bulk check \"$LICENSE\": "
    cat var/no_version.json | \
        jq '.no_versions'   | \
        jq -r "with_entries(select(.key == \"$LICENSE\"))" | \
        jq -r .[].aliases[] | \
        while read LINE;
        do
            printf "license\n$LINE\n"
        done | \
            ./devel/flame shell -s | \
            while read LINE
            do
                if [ "$LINE" == "" ]
                then
                    continue
                elif [ "$LINE" != "$EXPECTED" ]
                then
                    echo "ERROR"
                    echo " * license:  $LICENSE"
                    echo " * actual:   $LINE"
                    echo " * expected: $EXPECTED"
                    exit 1
                fi
            done
    echo OK
}

bulk_check_mutliple()
{
    LICENSE="$1"
    EXPECTED="$2"

    printf "%-${COL_SIZE}s" "Bulk check ANDed \"$LICENSE\": "
    ANDED_LIC=$(cat var/no_version.json | \
                    jq '.no_versions'   | \
                    jq -r "with_entries(select(.key == \"$LICENSE\"))" | \
                    jq -r .[].aliases[] | \
                    while read LINE;
                    do
                        printf "$LINE AND "
                    done | sed 's,AND $,,g')

    export BIG_LICENSE=""
    for i in $(seq 1 100)
    do
        BIG_LICENSE="$ANDED_LIC AND $BIG_LICENSE"
    done 
    BIG_LICENSE=$(echo $BIG_LICENSE | sed 's,AND[ ]*$,,g')
    RES=$(./devel/flame license $BIG_LICENSE)
    if [ "$RES" != "$EXPECTED" ]
    then
        echo "ERROR"
        echo " * license:  $BIG_LICENSE"
        echo " * actual:   $RES"
        echo " * expected: $EXPECTED"
        exit 1
    fi
    echo "OK"
    #.... with $(echo $BIG_LICENSE | wc -c) characters long license expression :)"
}

bulk_check_singles "GNU Lesser General Public License" \
                   "LGPL-2.0-only OR LGPL-2.1-only OR LGPL-3.0-only" 

bulk_check_mutliple "GNU Lesser General Public License" \
                    "LGPL-2.0-only OR LGPL-2.1-only OR LGPL-3.0-only" 
