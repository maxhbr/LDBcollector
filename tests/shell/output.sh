#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# simple script to make sure the formatters are working from main
#

PYTHONPATH=./python

RET=0
set -o pipefail

declare -A FORMAT_CHECK

FORMAT_CHECK["json"]="jq ."
FORMAT_CHECK["yaml"]="yamllint -c tests/yamllint.conf -"
FORMAT_CHECK["txt"]="xargs file"

verbose()
{
    echo "$*" 1>&2
}

verbosen()
{
    echo -n "$*" 1>&2
}

doflame()
{
    format=$1
    format_fun=$2
    command=$3

    verbosen " * $command: "
    $command | $format_fun > /dev/null
    if [ $? -ne 0 ]
    then
        verbose failed, checking format with $format_fun
        verbose "try: $command | $format_fun "
        exit 1
    fi
    verbose "OK"
}

for format in json yaml 
do
    format_fun=${FORMAT_CHECK[$format]}
    verbose "Format: $format (\"$format_fun\")"
    doflame "$format" "$format_fun" "flame -of $format aliases"
    doflame "$format" "$format_fun" "flame -of $format compats"
    doflame "$format" "$format_fun" "flame -of $format licenses"
    doflame "$format" "$format_fun" "flame -of $format operators"
    doflame "$format" "$format_fun" "flame -of $format license MIT"
    doflame "$format" "$format_fun" "flame -of $format compat MIT"
done
