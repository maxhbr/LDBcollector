#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

if [ -z "$1" ]; then
    echo 'Usage: generate-license.sh <li:id>'
    exit 1
fi

if [ ! -s $DIR/../data/$1.turtle ]; then
    echo Unknown license identifier, $DIR/../data/$1.turtle not found.
    exit 1
fi

if [ ! -x `which rdf`"" ]; then
    echo "rdf command not found."
    exit 1
fi

cd $DIR/../site/publish/id
rdf serialize $DIR/../data/$1.turtle >> $1.triples

if [ -s $DIR/../upstream/rdf/$1.rdf ]; then
    rdf serialize $DIR/../upstream/rdf/$1.rdf >> $1.triples
fi

$DIR/../build/publish-json.rb $1.triples $1.json ../context.json
$DIR/../build/publish-rdf.rb $1.triples $1.rdf ../context.json
rm $1.triples

