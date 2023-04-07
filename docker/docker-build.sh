#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

cat <<EOF >.dockerignore
$(cat .gitignore)
docker
EOF

podman build --tag maxhbr/ldbcollector -f docker/Dockerfile .

times