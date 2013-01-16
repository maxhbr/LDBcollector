#!/bin/bash

EXPRESSO=node_modules/expresso/bin/expresso

if [ ! -x $EXPRESSO ]; then
    EXPRESSO=`which expresso`
fi

if [ ! -x $EXPRESSO ]; then
    echo "Cannot find expresso, please install it with:"
    echo ""
    echo "    npm install -g expresso"
    echo ""
    exit 1
fi

$EXPRESSO src/server/tests/*js
