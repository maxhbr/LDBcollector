#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PORT=3001
if [[ "$#" -eq 1 && "$1" == "--help" ]]; then
    cat <<EOF
usage:
  $0 [tag]

This
 - runs the docker image
   - mounts ./data into the container as a volume
   - runs the server
   - exposes it on port=$PORT
EOF
    exit 0
fi

docker="docker"
tag="${1:-maxhbr/ldbcollector:latest}"
if command -v "podman" &> /dev/null; then
  >&2 echo "INFO: use podman"
  docker="podman"
  tag="${1:-localhost/maxhbr/ldbcollector:latest}"
fi

if [[ -z "$("$docker" images -q "$tag" 2> /dev/null)" ]]; then
    &>2 echo "WARN: was not able to find '$tag' in '$docker' registry, try to pull it"
    $docker pull "$tag"
fi

$docker run -it \
    -v "$(pwd)/data":/ldbcollector/data \
    --env PORT=$PORT \
    -p "$PORT:$PORT" \
    "$tag"

