#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

docker="docker"
tag="${1:-maxhbr/ldbcollector:latest}"
if command -v "podman" &> /dev/null; then
  >&2 echo "use podman"
  docker="podman"
  tag="${1:-localhost/maxhbr/ldbcollector:latest}"
fi

$docker run -it \
    -v "$(pwd)/data":/ldbcollector/data \
    --env PORT=3001 \
    -p "3001:3001" \
    "$tag"

