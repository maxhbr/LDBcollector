#!/usr/bin/env bash

set -euo pipefail

datadir="$1"
oldtag="$2"
newtag="$3"

cd $datadir

cat <<EOF | docker build --tag "$newtag" -f - .
FROM $oldtag
LABEL org.opencontainers.image.source="https://github.com/maxhbr/ldbcollector"
ADD . /ldbcollector/data
EOF