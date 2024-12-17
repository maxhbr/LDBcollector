#!/bin/bash

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


THIS_FILE=${BASH_SOURCE[0]}
RET=0
LICENSE_ERRORS=""
set -o pipefail

check_test_case()
{
    echo -n "Check test cases: "
    RESULT="OK"
    for lf in `ls var/licenses/*.json`; 
    do 
        LICENSE_NAME=$(echo $lf | sed -e 's/\.json//g' -e 's,[/]*var/licenses[/]*,,g')
        TEST_EXIST=$(cat $THIS_FILE | grep check_presence | grep -w $LICENSE_NAME | grep -v "^#" | wc -l)
        echo -n "$LICENSE_NAME: "
        if [ $TEST_EXIST -eq 0 ]
        then
            LICENSE_ERRORS="$LICENSE_NAME is missing test case."
            echo missing
            RET=1
        else
            echo "OK"
        fi
    done
    echo "$RESULT"
}

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
            LICENSE_ERRORS="$LICENSE_ERRORS $LICENSE_FILE missing, "
        fi
        jq . $lf > /dev/null
        if [ $? -ne 0 ]
        then
            echo "FAIL: $lf not in JSON format"
            RET=$(( $RET + 1 ))
            RESULT=" FAIL"
            LICENSE_ERRORS="$LICENSE_ERRORS $lf not in JSON format, "
        fi
    done
    
    # all LICENSE files should have a JSON file
    for lf in `find var/licenses -name "*.LICENSE"`; 
    do JSON_FILE=`echo $lf | sed -e 's/\.LICENSE/\.json/g'` ; 
       ls $JSON_FILE > /dev/null
       if [ $? -ne 0 ]
       then
           echo "FAIL $lf file missing"
           RET=$(( $RET + 1 ))
           RESULT=" FAIL"
           LICENSE_ERRORS="$LICENSE_ERRORS $lf file missing, "
       fi
    done
    echo "$RESULT"
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
        LICENSE_ERRORS="$LICENSE_ERRORS  $REG_EXP_PRESENCE not present in $FILE"
    fi

    # check unpresence
    if [ "$REG_EXP_UNPRESENCE" != "" ]
    then
        UNPRESENT=$(echo "cat $FILE | jq  -r .aliases[] | grep $REG_EXP_UNPRESENCE" | bash )
        if [ "$UNPRESENT" != "" ]
        then
            echo "FAIL"
            echo " * cause: Incorrectly present in $FILE"
            echo " --------------------------"
            echo "Should be unpresent: \"$UNPRESENT\""
            echo " --------------------------"
            RET=$(( $RET + 1 ))
            _RET="FAIL"
            LICENSE_ERRORS="$LICENSE_ERRORS  \"$REG_EXP_UNPRESENCE\" incorrectly found in \"$FILE\""
        fi
    fi
    
    if [ "$_RET" = "OK" ]
    then
        echo OK
    else
        echo FAILURE
    fi
}


check_test_case

# below is performed in Makefile
# check_file_presence
# check_schema

ZERO_BSD_PRESENT=" -e 0BSD -i -e zero -e \"0-\" -e \" 0 \" -e \"0C\" -e \"free[ -]public\""
BSD2_PRESENT=" -e 2 -i -e two -e simplified -e freebsd "
BSD2_PATENT_PRESENT=" -i -e patent" 
BSD3_PRESENT=" -e 3 -i -e new -e modified -e revised -e three -e 'no advertising' -e EDL -e eclipse -e 2.0 "
BSD4_PRESENT=" -e 4 -i -e 'BSD with advertising' -e original "

check_presence AAL " -i -e AAL -e Attribution " ""
check_presence AFL-1.1 " -e 1.1 " "-e 2. -e 1.2  -e 3"
check_presence AFL-1.2 " -e 1.2 " "-e 2. -e 1.1  -e 3"
check_presence AFL-2.0 " -e 2.0 " "-e 1 -e 2.1 -e 3"
check_presence AFL-2.1 " -e 2.1 " "-e 1. -e 2.0 -e 0  -e 3"
check_presence AFL-3.0 " -e 3 " "-e 1 -e 2 "

check_presence AGPL-3.0-only     " -i -e 3 -e affero" " -e '1 ' -e 2 -e later -e plus -e + -e library -e lesser "
check_presence AGPL-3.0-or-later " -e 3 -e later -e +" " -e '1 ' -e 2  -e library -e lesser "

check_presence Apache-1.0 " -e 1.0" "-e 2 -e 1.1"
check_presence Apache-1.1 " -e 1.1" "-e 2 -e 1.0"
check_presence Apache-2.0 " -e 2" "-e 1"

check_presence APSL-2.0 " -e 2" "-e 1 -e [3-9]"

check_presence Artistic-1.0 " -e 1.0 -e 1" "-e 2 "
check_presence Artistic-2.0 " -e 2 -e 2.0 " "-e 1"

check_presence Autoconf-exception-2.0 " -e autoconf " " -e 3"
check_presence Autoconf-exception-3.0 " -e autoconf " " -e 2"

check_presence Beerware " -i -e beer " ""
check_presence Bitstream-Vera " -i -e bitstream " ""
check_presence blessing " -i -e blessing " ""
check_presence BlueOak-1.0.0  " -i -e 1 -e model" " -e 2"
check_presence Bootloader-exception " -i bootloader" ""
check_presence BSL-1.0                            " -e BSL-1 -e BSL1 -e 1 " " -i -e original "

check_presence LicenseRef-scancode-boost-original " -i -e original "        " -e BSL-1 -e BSL1 -e 1 "  
check_presence LicenseRef-scancode-ssleay " -i -e leay "        " -e openssl"  

check_presence 0BSD "$ZERO_BSD_PRESENT" "$BSD3_PRESENT $BSD2_PRESENT "
check_presence BSD-1-Clause " -i BSD" " -e 2 -e 3 -e 4 "
check_presence BSD-2-Clause "$BSD2_PRESENT" "$ZERO_BSD_PRESENT $BSD3_PRESENT "
check_presence BSD-2-Clause-Patent "$BSD2_PATENT_PRESENT" "$ZERO_BSD_PRESENT $BSD3_PRESENT "
check_presence BSD-2-Clause-Views " -i -e view"  " -e 0 -e 1 -e 3 -e 4"
check_presence BSD-3-Clause "$BSD3_PRESENT" "$ZERO_BSD_PRESENT  -i -e two -e simplified -e freebsd "
check_presence BSD-3-Clause-Clear " -i -e clear" " -e 0 -e 1 -e 2 -e 4"
check_presence BSD-3-Clause-Modification " -i -e modification -e repoze " " -e 0 -e 1 -e 2 -e 4"
check_presence BSD-3-Clause-No-Nuclear-Warranty " -i -e nuclear" " -e 0 -e 1 -e 2 -e 4"
check_presence BSD-4-Clause "$BSD4_PRESENT" " $ZERO_BSD_PRESENT $BSD2_PRESENT $BSD3_PRESENT"
check_presence BSD-4-Clause-UC " -i -e university -e UC" " -e 1 -e 2 -e 3"
check_presence BSD-Source-Code " -i -e source -e code " " -e 1 -e 2 -e 3"

check_presence bzip2-1.0.6 " -i -e 1.0.6 -e 2010  -e bzip2 " " 1.1"

check_presence CC0-1.0 " -e 1 -e 0 " " -e [2-9]"
check_presence CC-PDDC " -i -e pd -e dedication  " " -e [1-9]"
check_presence CC-BY-3.0 " -e 3 " " -e 4"
check_presence CC-BY-4.0 " -e 4 " " -e 3"
check_presence CC-BY-SA-2.5 " -e 2.5 " " -e 3 -e 4"
check_presence CC-BY-SA-3.0 " -e 3.0 " " -e 2 -e 4"
check_presence CC-BY-SA-4.0 " -e 4 " " -e 2 -e 3"

check_presence CDDL-1.0 " -e 1.0 " " -e 1.1"
check_presence CDDL-1.1 " -e 1.1" " -e 1.0"

check_presence CECILL-B " -i -e cecill-b -e cecill\ b" " -e -A -e -C"
check_presence CECILL-C " -i -e cecill-c -e cecill\ c" " -e -A -e -B"
check_presence CECILL-2.1 " -i -e cecill-2.1 -e 2.1" " -e -A -e -B -e -C"

check_presence CNRI-Python " -i -e CNRI  " ""
check_presence CPL-1.0 " -e 1.0  -e 1 " " -e 0.5 -e 2"

check_presence Classpath-exception-2.0 " -i -e classpath " " -e 1"
check_presence curl " -i -e curl " ""

check_presence dtoa " -i -e dtoa -e x11 -e MIT" ""

check_presence DocBook-XML " -i -e dmit -e docbook " ""

check_presence ECL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence ECL-2.0 " -e 2.0 -e 2" " -e 1"
check_presence EFL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence EFL-2.0 " -e 2.0 -e 2" " -e 1"

check_presence EPL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence EPL-2.0 " -e 2.0 -e 2" " -e 1"

check_presence EUPL-1.0 " -e 1.0 -e 1" " -e 2"
check_presence EUPL-1.1 " -e 1.1 -e 1" " -e 2"
check_presence EUPL-1.2 " -e 1.2 -e 1" " -e 0"

check_presence FSFAP    " -i -e FSFAP -e \"All Permissive\" -e fsf-ap"       " -i -e FUL"
check_presence FSFUL    " -i  -e FSFUL -e unlimited -e fsf-free "      " -e FSFAP -e FSFFULLR -e FSFULLRWD "
check_presence FSFULLR  " -i -e FSFULLR -e unlimited -e retention "    " -e FSFAP -e FSFULLRWD "
check_presence FSFULLRWD " -i -e FSFULLRWD -e warranty " " -e FSFAP  "

check_presence FTL " -i -e FTL -e freetype " ""

check_presence GCC-exception-3.1 " -e GCC -e 3" " -e 2 "
GPL_COMMON_EXCL=" -e lgpl -e library -e lesser -e affero -e agpl"
check_presence GPL-1.0-only " -e 1 " " -e 2 -e later -e 3 $GPL_COMMON_EXCL "
check_presence GPL-2.0-only " -e 2 " " -e '1 ' -e later -e 3  $GPL_COMMON_EXCL  "
check_presence GPL-3.0-only " -e 3 " " -e '1 ' -e 2 -e later -i  $GPL_COMMON_EXCL "

check_presence GPL-1.0-or-later " -e 1 -e later" " -e 2 -e 3 $GPL_COMMON_EXCL  "
check_presence GPL-2.0-or-later " -e 2 -e later" " -e '1 ' -e 3 $GPL_COMMON_EXCL "
check_presence GPL-3.0-or-later " -e 3 -e later" " -e '1 ' -e 2 $GPL_COMMON_EXCL "

check_presence HPND " -i -e hpnd -e historic" ""

check_presence ICU " -i -e icu " ""
check_presence IJG " -i -e ijg -e independent -e jpeg " " -e short"
check_presence IJG-short " -i -e ijg -e independent -e jpeg  " ""
check_presence IPL-1.0 " -i -e ipl -e ibm   " ""
check_presence Intel " -i -e intel " " -e 0 -e 1 -e 2 -e 3 -e 4 "
check_presence ISC " -i -e isc  " ""

check_presence JSON " -i -e JSON  " ""

check_presence Latex2e " -i -e latex2  " ""

LGPL_COMMON=" -e lgpl -e lesser -e library -e affero "
check_presence LGPL-2.0-only " $LGPL_COMMON -e 2.0 -e 2 " " -e 3  -e later"
check_presence LGPL-2.0-or-later " $LGPL_COMMON -e 2.0 -e 2 -e later " " -e 3"
check_presence LGPL-2.1-only " $LGPL_COMMON -e 2.1 " " -e 3  -e later"
check_presence LGPL-3.0-only " $LGPL_COMMON -e 3 " " -e 2  -e later"

check_presence LGPL-2.1-or-later " $LGPL_COMMON -e 2 -e later" " -e 3"
check_presence LGPL-3.0-or-later " $LGPL_COMMON -e 3 -e later" " -e 2"

check_presence LicenseRef-scancode-boost-original " -i -e original " ""
check_presence LicenseRef-scancode-cvwl " -i -e cvwl -e MITRE " ""
check_presence LicenseRef-scancode-g10-permissive " -i -e  g10 " ""
check_presence LicenseRef-scancode-indiana-extreme " -i -e indiana " " -e 1.2"
check_presence LicenseRef-scancode-iso-8879 " -i 8879 " ""
check_presence LicenseRef-scancode-josl-1.0 " -i josl-1 -e jabber " ""
check_presence LicenseRef-scancode-public-domain " -i -e domain -e public " ""
check_presence LicenseRef-scancode-wtfpl-1.0 " -i -e wtfpl " ""
check_presence LicenseRef-scancode-xfree86-1.0 " -i -e xfree86 " ""
check_presence LicenseRef-scancode-zpl-1.0 "-i -e zpl" ""

check_presence Libpng " -i -e libpng -e PNG  " " -e 2 "
check_presence libpng-2.0 " -i -e libpng -e PNG  " ""
check_presence libtiff " -i -e tiff  " ""
check_presence Libtool-exception " -i -e libtool  " ""
check_presence Linux-syscall-note " -i -e syscall  " ""
check_presence LLVM-exception " -i -e llvm  " ""

check_presence MirOS " -i -e MirOS -e mir-os" ""

check_presence MIT " -i -e MIT -e Expat" " -i -e 0 -e we -e advert -e modern "
check_presence MIT-0 " -e 0 -i -e \"no attribution\"" " -i -e we -e advert -e modern -e wu"
check_presence MIT-advertising " -e 0 -i -e advertising -e enlighten" " -i -e \"no advertising\" -e wu -e 0 -e modern"
check_presence MIT-Modern-Variant " -i -e modern" " -i -e advertising -e 0 -e wu"
check_presence MIT-open-group " -i -e opengroup -e open-group -e open\ group " " -i -e advertising -e modern -e 0 "
check_presence MIT-Wu " -i -e wu -e addition " " -i -e advertising -e modern -e 0 "
check_presence MITNFA " -i -e  false -e nfa " " -i -e advertising -e modern -e 0 -e wu "
check_presence Motosoto " -i -e  motosoto " ""

check_presence MPL-1.0 " -e 1.0" "-e 2 -e 1.1"
check_presence MPL-1.1 " -e 1.1" "-e 2 -e 1.0"
check_presence MPL-2.0 " -e 2" " -e 1"
check_presence MPL-2.0-no-copyleft-exception " -i -e 2 -e 'no[ \-]copyleft'" "-e 1"

check_presence MulanPSL-1.0 " -e 1" " -e 2"
check_presence MulanPSL-2.0 " -e 2" " -e 1"

check_presence NAIST-2003 " -i -e naist -e nara " ""
check_presence NASA-1.3 " -i -e nasa " ""
check_presence NCSA " -i -e ncsa -e illinois " ""
check_presence NGPL " -i -e ngpl -e nethack" ""
check_presence Nokia " -i -e nokia -e nokos " ""
check_presence NTP " -i -e ntp -e network " ""

check_presence OCaml-LGPL-linking-exception " -i -e ocaml" ""
check_presence ODC-By-1.0 " -i -e 1.0 -e odc" ""
check_presence OFL-1.0 " -e 1.0" " -e 1.1"
check_presence OFL-1.1 " -e 1.1" " -e 1.0"
check_presence OGTSL " -i -e ogtsl -e Open\ Group -e ogts\ license -e opengroup" ""
check_presence OML " -i -e oml -e market -e fastcgi -e OM\ License" ""
check_presence OpenSSL " -i -e openssl " ""
check_presence OSL-3.0 " -i -e Open\ Software -e OSL-3 -e OSL\ 3" ""

check_presence Plexus " -i -e plexus -e classworlds " ""
check_presence PostgreSQL " -i -e postgresql " ""
check_presence Python-2.0.1 " -i -e Python " ""

check_presence RSA-MD " -i -e RSA " ""
check_presence RSCPL " -i -e RSCPL -e Ricoh " ""

check_presence SAX-PD " -i -e SAX -e xmlpull " ""
check_presence Sendmail " -i -e sendmail " ""
check_presence SGI-B-2.0 " -i -e SGI " ""
check_presence Sleepycat " -i -e sleepycat -e Berkeley " ""
check_presence SPL-1.0 " -i -e sun -e spl" ""
check_presence SSPL-1.0 " -i -e SSPL -e server\ side" ""
check_presence SunPro " -i -e SunPro " ""
check_presence SMLNJ " -i -e smlnj -e Jersey -e nj " ""
check_presence SWL " -i -e SWL -e Scheme\ Widget" ""

check_presence TCL " -i -e tcl " ""
check_presence TU-Berlin-1.0 " -e 1 -e berlin" " -e 2"
check_presence TU-Berlin-2.0 " -e 2" " -e 1"

check_presence UnixCrypt " -i -e unixcrypt" ""
check_presence Unlicense " -i -e unlicense  -e unli[n]cence " ""
check_presence UPL-1.0 " -i -e upl -e universal" ""

check_presence Vim " -i -e vim" ""
check_presence VSL-1.0 " -i -e VSL -e Vovida" " -e 2"

check_presence W3C " -i -e w3c -e w3.org " " -e 1998 -e 2015 "
check_presence W3C-19980720 " 1998 " " -e 2015 "
check_presence W3C-20150513 " 2015 " " -e 1998 "
check_presence WTFPL " -i -e WTFPL -e what -e wtf\ p" ""

check_presence X11 " -i -e 11 -e 'consortium' -e 'X ' -e 'X/MIT' -e MIT-X" "" 
check_presence X11-distribute-modifications-variant " -i -e modifications -e fsf" ""
check_presence x11-keith-packard " -i -e packard -e hpnd " ""
check_presence Xfig " -i -e Xfig" ""
check_presence Xnet " -i -e Xnet -e altera -e x.net" ""
check_presence xpp " -i -e xpp -e indiana " ""

check_presence LicenseRef-scancode-xfree86-1.0 " -i -e 1.0 " " -e  X/MIT -e 1.1 " 
check_presence XFree86-1.1 " -i -e 1.1 " " -e  X/MIT -e 1.0 " 

check_presence Zlib " -i -e libz -e zlib" " -i bsd "
check_presence ZPL-1.1 " -e 1.1" " -e 2"
check_presence ZPL-2.0 " -e 2.0" " -e 1 -e 2.1"
check_presence ZPL-2.1 " -e 2.1" " -e 1.1 -e 2.0"


if [ $RET -ne 0 ]
then
    echo ""
    echo "License errors"
    echo "$LICENSE_ERRORS"
    echo 
fi

exit $RET
