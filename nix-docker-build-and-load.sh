#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ "$#" -eq 1 && "$1" == "--help" ]]; then
    cat <<EOF
usage:
  $0
  $0 echo-output   -> just echo the output file, that will be generated
  $0 echo-tag      -> just echo the tag, that the image will have in the local registry
  $0 run           -> run the server after build, using ./docker-run.sh

This
 - builds the image using nix
 - loads the image into the local docker registry
 - optionally runs the image
EOF
    exit 0
fi

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

