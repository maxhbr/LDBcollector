#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd "$DIR/../../upstream/rdf"

DATA_HOME="${HOME}/.local/share"
if [ -n "${XDG_DATA_HOME}" ]; then
    DATA_HOME="${XDG_DATA_HOME}"
fi

PYTHON="${DATA_HOME}/licensedb/virtualenv/bin/python"

$PYTHON ../../src/build/rdfa.py

