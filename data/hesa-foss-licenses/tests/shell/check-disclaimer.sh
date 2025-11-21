#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

PROD_DISCLAIMERS=$(find . -name "*.json" | xargs grep disclaimer | grep http | cut -d : -f 3-10 | sort  -u | wc -l)
TEST_DISCLAIMERS=$(find . -name "*.json" | xargs grep disclaimer | grep test | cut -d : -f 3-10 | sort  -u | wc -l)


EXIT_CODE=0
if [ $PROD_DISCLAIMERS -ne 1 ]
then
    echo "Number of production disclaimers ($PROD_DISCLAIMERS) incorrect. Should be 1"
    EXIT_CODE=1
fi

if [ $PROD_DISCLAIMERS -ne 1 ]
then
    echo "Number of production disclaimers ($PROD_DISCLAIMERS) incorrect. Should be 1"
    EXIT_CODE=1
fi


EXPECTED="\"https://raw.githubusercontent.com/hesa/foss-licenses/main/var/disclaimer.md\""
ACTUAL="$(find . -name "*.json" | xargs grep disclaimer | grep http | cut -d : -f 3-10 | head -1 | sed 's/[, ]*//g')"
if [ "$EXPECTED" != "$ACTUAL" ]
then
    echo "Production disclaimer URL incorrect"
    echo " * expected: $EXPECTED"
    echo " * actual:   $ACTUAL"
    
    EXIT_CODE=1
fi
    
EXPECTED="\"This is TEST data. DO NOT USE\""
ACTUAL="$(find . -name "*.json" | xargs grep disclaimer | grep test | cut -d : -f 3-10 | head -1  | sed -e 's/^ //g' -e 's/,$//g')"
if [ "$EXPECTED" != "$ACTUAL" ]
then
    echo "Test disclaimer URL incorrect"
    echo " * expected: $EXPECTED"
    echo " * actual:   $ACTUAL"
    EXIT_CODE=1
fi
    
if [ $EXIT_CODE -ne 0 ]
then
    echo " **********************************************"
    echo " ******************* ERROR ********************"
    echo " **********************************************"
fi
exit $EXIT_CODE
