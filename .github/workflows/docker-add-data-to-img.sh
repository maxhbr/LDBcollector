#!/usr/bin/env bash

set -euo pipefail

datadir="$1"
oldtag="$2"
newtag="$3"

docker="docker"
if command -v "podman" &> /dev/null; then
  >&2 echo "use podman"
  docker="podman"
fi

cd $datadir


cat <<EOF | $docker build --tag "$newtag" -f - .
FROM $oldtag
LABEL org.opencontainers.image.source="https://github.com/maxhbr/ldbcollector"
ADD . /ldbcollector/data
EOF