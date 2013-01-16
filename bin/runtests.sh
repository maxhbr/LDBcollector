#!/bin/bash

MOCHA=node_modules/mocha/bin/mocha

if [ ! -x $MOCHA ]; then
    MOCHA=`which mocha`
fi

if [ ! -x $MOCHA ]; then
    echo "Cannot find mocha, please install it with:"
    echo ""
    echo "    npm install -g mocha"
    echo ""
    exit 1
fi

$MOCHA --reporter spec src/server/tests/*js
