#!/bin/bash

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


RET=0
set -o pipefail

check_file_presence()
{
    echo -n "Check file presence: "
    RESULT="OK"
    # all JSON files should have a LICENSE file
    for lf in `find var/licenses -name "*.json"`; 
    do 
        LICENSE_FILE=`echo $lf | sed 's/\.json/\.LICENSE/g'` ; 
        ls $LICENSE_FILE > /dev/null
        if [ $? -ne 0 ]
        then
            echo "FAIL: $LICENSE_FILE missing"
            RET=$(( $RET + 1 ))
            RESULT=" FAIL"

        fi
        jq . $lf > /dev/null
        if [ $? -ne 0 ]
        then
            echo "FAIL: $lf not in JSON format"
            RET=$(( $RET + 1 ))
            RESULT=" FAIL"
        fi
    done
    
    # all LICENSE files should have a JSON file
    for lf in `find var/licenses -name "*.LICENSE"`; 
    do JSON_FILE=`echo $lf | sed 's/\.LICENSE/\.json/g'` ; 
       ls $JSON_FILE > /dev/null
       if [ $? -ne 0 ]
       then
           echo "FAIL $lf file missing"
           RET=$(( $RET + 1 ))
           RESULT=" FAIL"
       fi
    done
    echo "$RESULT"

}

check_schema()
{
    # Make sure schema is valid JSON
    echo -n "License schema: " ; 
    jq . var/license_schema.json > /dev/null 
    if [ $? -ne 0 ]
    then
        echo FAIL;
        RET=$(( $RET + 1 ))
    fi
    echo "OK" 
}

check_presence()
{
    LICENSE=$1
    FILE=var/licenses/$LICENSE.json

    REG_EXP_PRESENCE="$2"
    REG_EXP_UNPRESENCE="$3"

    _RET="OK"

    # check presence
    #echo "cat $FILE | jq  -r .aliases[] | grep -v $REG_EXP_PRESENCE )" | bash
    PRESENT=$(echo "cat $FILE | jq  -r .aliases[] | grep -v $REG_EXP_PRESENCE" | bash )
    echo -n "$LICENSE: "
    if [ "$PRESENT" != "" ]
    then
        echo "FAIL"
        echo " * cause: Not present in $FILE"
        echo " --------------------------"
        echo "Should be present: $REG_EXP_PRESENCE"
        echo " --------------------------"
        RET=$(( $RET + 1 ))
        _RET="FAIL"
    fi

    # check unpresence
    if [ "$REG_EXP_UNPRESENCE" != "" ]
    then
        UNPRESENT=$(echo "cat $FILE | jq  -r .aliases[] | grep $REG_EXP_UNPRESENCE" | bash )
        if [ "$UNPRESENT" != "" ]
        then
            echo "FAIL"
            echo " * cause: Incorrectly not present in $FILE"
            echo " --------------------------"
            echo "Unpresent: \"$UNPRESENT\""
            echo " --------------------------"
            RET=$(( $RET + 1 ))
            _RET="FAIL"
        fi
    fi
    
    if [ "$_RET" = "OK" ]
    then
        echo OK
    else
        exit 1
    fi
}

#check_file_presence
#check_schema


ZERO_BSD_PRESENT=" -e 0BSD -i -e zero -e \"0-\""
BSD2_PRESENT=" -e 2 -i -e two -e simplified -e freebsd "
BSD2_PATENT_PRESENT=" -i -e patent" 
BSD3_PRESENT=" -e 3 -i -e new -e modified -e revised -e three -e 'no advertising' "
BSD4_PRESENT=" -e 4 -i -e 'BSD with advertising' -e original "

check_presence AFL-1.1 " -e 1.1 " "-e 2. -e 1.2  -e 3"
check_presence AFL-1.2 " -e 1.2 " "-e 2. -e 1.1  -e 3"
check_presence AFL-2.0 " -e 2.0 " "-e 1 -e 2.1 -e 3"
check_presence AFL-2.1 " -e 2.1 " "-e 1. -e 2.0 -e 0  -e 3"
check_presence AFL-3.0 " -e 3 " "-e 1 -e 2 "

check_presence Apache-1.0 " -e 1.0" "-e 2 -e 1.1"
check_presence Apache-1.1 " -e 1.1" "-e 2 -e 1.0"
check_presence Apache-2.0 " -e 2" "-e 1"

check_presence APSL-2.0 " -e 2" "-e 1 -e [3-9]"

check_presence Artistic-1.0 " -e 1.0 -e 1" "-e 2 "
check_presence Artistic-2.0 " -e 2 -e 2.0 " "-e 1"

check_presence BSL-1.0                            " -e BSL-1 -e BSL1 -e 1 " " -i -e original "
check_presence LicenseRef-scancode-boost-original " -i -e original "        " -e BSL-1 -e BSL1 -e 1 "  

check_presence 0BSD "$ZERO_BSD_PRESENT" "$BSD3_PRESENT $BSD2_PRESENT "
check_presence BSD-2-Clause "$BSD2_PRESENT" "$ZERO_BSD_PRESENT $BSD3_PRESENT "
check_presence BSD-2-Clause-Patent "$BSD2_PATENT_PRESENT" "$ZERO_BSD_PRESENT $BSD3_PRESENT "
check_presence BSD-2-Clause-Views " -i -e view"  " -e 0 -e 1 -e 3 -e 4"
check_presence BSD-3-Clause "$BSD3_PRESENT" "$ZERO_BSD_PRESENT $BSD2_PRESENT"
check_presence BSD-3-Clause-Clear " -i -e clear" " -e 0 -e 1 -e 2 -e 4"
check_presence BSD-4-Clause "$BSD4_PRESENT" " $ZERO_BSD_PRESENT $BSD2_PRESENT $BSD3_PRESENT"

check_presence CC0-1.0 " -e 1 -e 0 " " -e [2-9]"
check_presence CC-PDDC " -i -e pd -e dedication  " " -e [1-9]"
check_presence CC-BY-3.0 " -e 3 " " -e 4"
check_presence CC-BY-4.0 " -e 4 " " -e 3"
check_presence CC-BY-SA-2.5 " -e 2.5 " " -e 3 -e 4"
check_presence CC-BY-SA-3.0 " -e 3.0 " " -e 2 -e 4"
check_presence CC-BY-SA-4.0 " -e 4 " " -e 2 -e 3"

check_presence CDDL-1.0 " -e 1.0 " " -e 1.1"
check_presence CDDL-1.1 " -e 1.1" " -e 1.0"

check_presence CPL-1.0 " -e 1.0  -e 1 " " -e 0.5 -e 2"

check_presence EFL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence EFL-2.0 " -e 2.0 -e 2" " -e 1"

check_presence EPL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence EPL-2.0 " -e 2.0 -e 2" " -e 1"

check_presence FSFAP    " -i -e FSFAP -e \"All Permissive\" -e fsf-ap"       " -i -e FUL"
check_presence FSFUL    " -i  -e FSFUL -e unlimited -e fsf-free "      " -e FSFAP -e FSFFULLR -e FSFULLRWD "
check_presence FSFULLR  " -i -e FSFULLR -e unlimited -e retention "    " -e FSFAP -e FSFULLRWD "
check_presence FSFULLRWD " -i -e FSFULLRWD -e warranty " " -e FSFAP  "

check_presence GPL-1.0-only " -e 1 " " -e 2 -e later -e 3"
check_presence GPL-2.0-only " -e 2 " " -e '1 ' -e later -e 3"
check_presence GPL-3.0-only " -e 3 " " -e '1 ' -e 2 -e later -i -e affero "

check_presence GPL-1.0-or-later " -e 1 -e later" " -e 2 -e 3"
check_presence GPL-2.0-or-later " -e 2 -e later" " -e '1 ' -e 3"
check_presence GPL-3.0-or-later " -e 3 -e later" " -e '1 ' -e 2"

check_presence AGPL-3.0-only     " -e 3 " " -e '1 ' -e 2 -e later -e plus -e +"
check_presence AGPL-3.0-or-later " -e 3 -e later -e +" " -e '1 ' -e 2"

check_presence IJG " -i -e ijg -e independent -e jpeg " ""

check_presence LGPL-2.0-only " -e 2.0 -e 2 " " -e 3  -e later"
check_presence LGPL-2.1-only " -e 2.1 " " -e 3  -e later"
check_presence LGPL-3.0-only " -e 3 " " -e 2  -e later"

check_presence LGPL-2.1-or-later " -e 2 -e later" " -e 3"
check_presence LGPL-3.0-or-later " -e 3 -e later" " -e 2"

check_presence LicenseRef-scancode-g10-permissive " -i -e  g10 " ""

check_presence MIT " -i -e MIT -e Expat" " -e 0"
check_presence MIT-0 " -e 0 -i -e \"no attribution\"" ""
check_presence MIT-advertising " -e 0 -i -e advertising" " -i -e \"no advertising\""

check_presence MPL-1.0 " -e 1.0" "-e 2 -e 1.1"
check_presence MPL-1.1 " -e 1.1" "-e 2 -e 1.0"
check_presence MPL-2.0 " -e 2" " -e 1"
check_presence MPL-2.0-no-copyleft-exception " -i -e 2 -e 'no[ \-]copyleft'" "-e 1"

check_presence OFL-1.0 " -e 1.0" " -e 1.1"
check_presence OFL-1.1 " -e 1.1" " -e 1.0"

check_presence TU-Berlin-1.0 " -e 1" " -e 2"
check_presence TU-Berlin-2.0 " -e 2" " -e 1"

check_presence W3C " -i -e w3c -e w3.org " " -e 1998 -e 2015 "
check_presence W3C-19980720 " 1998 " " -e 2015 "
check_presence W3C-20150513 " 2015 " " -e 1998 "

check_presence X11 " -i -e 11 -e 'consortium' -e 'X ' -e 'X/MIT'" 

check_presence ZPL-1.1 " -e 1.1" " -e 2"
check_presence ZPL-2.0 " -e 2.0" " -e 1"
check_presence ZPL-2.1 " -e 2.1" " -e 1.1"




exit $RET
