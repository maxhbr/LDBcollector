#!/usr/bin/env bash

set -euo pipefail

datadir="$1"
oldtag="$2"
newtag="$3"

cd $datadir

cat <<EOF | $docker build --tag "$newtag" -f - .
FROM $oldtag
WORKDIR 
ADD . /ldbcollector/data
EOF