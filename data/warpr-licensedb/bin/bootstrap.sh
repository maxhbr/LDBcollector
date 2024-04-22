#!/bin/bash

function req {
    echo "virtualenv and pip are required, on debian or ubuntu you can install these with:"
    echo ""
    echo "    sudo apt-get install python-virtualenv python-pip"
    echo ""
    echo "A recent version of node.js or io.js is also required, see https://iojs.org/"
    echo ""
    exit 1
}

DATA_HOME="${HOME}/.local/share"
if [ -n "${XDG_DATA_HOME}" ]; then
    DATA_HOME="${XDG_DATA_HOME}"
fi

VIRTUALENV=`which virtualenv`
if [ -z "$VIRTUALENV" ]; then
    req
fi

PIP=`which pip`
if [ -z "$PIP" ]; then
    req
fi

NPM=`which npm`
if [ -z "$NPM" ]; then
    req
fi

$NPM install

$VIRTUALENV "${DATA_HOME}/licensedb/virtualenv"

PIP="${DATA_HOME}/licensedb/virtualenv/bin/pip"
if [ -x $PIP ]; then
    $PIP install --requirement=requirements.txt
else
    echo "There was an error installing the virtualenv."
    echo "Could not find pip at $PIP."
fi
