#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

output=ldbcollector.tar.gz
if [[ $# -eq 1 && "$1" == "echo-output" ]]; then
    echo "$output"
    exit 0
fi

docker="docker"
tag="maxhbr/ldbcollector:latest"
if command -v "podman" &> /dev/null; then
  >&2 echo "use podman"
  docker="podman"
  tag="localhost/maxhbr/ldbcollector:latest"
fi
if [[ $# -eq 1 && "$1" == "echo-tag" ]]; then
    echo "$tag"
    exit 0
fi

nix build -o "$output" .#ldbcollector-image                                                                                                         
$docker load --input "$output"

if [[ $# -eq 1 && "$1" == "run" ]]; then
    ./docker-run.sh "$tag"
fi

