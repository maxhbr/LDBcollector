#!/bin/bash

function req {
    echo "virtualenv and pip are required, on debian or ubuntu you can install these with:"
    echo ""
    echo "    sudo apt-get install python-virtualenv python-pip"
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

$VIRTUALENV "${DATA_HOME}/licensedb/virtualenv"

PIP="${DATA_HOME}/licensedb/virtualenv/bin/pip"
if [ -x $PIP ]; then
    $PIP install requests
else
    echo "There was an error installing the virtualenv."
    echo "Could not find pip at $PIP."
fi
