#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

exec_flame()
{
    ./devel/flame $*
}


test_flame()
{
    COMMAND="$1"
    LICENSE="$2"
    EXPECTED="$3"

    ACTUAL=$(exec_flame $COMMAND $LICENSE 2>/dev/null)

    echo -n " $COMMAND $LICENSE: "
    if [ "$ACTUAL" != "$EXPECTED" ]
    then
        echo "fail....."
        echo "  license : $LICENSE"
        echo "  expected: $EXPECTED" 
        echo "  actual:   $ACTUAL"
        exit 1
    fi
    echo "OK"
}


echo "Testing issues"
echo "=============="
echo " https://github.com/hesa/foss-licenses/issues/214"
echo "---------------------------------------------------"
test_flame license "GPL" "GPL"
