#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

tag="${1:-maxhbr/ldbcollector}"

cat <<EOF >.dockerignore
$(cat .gitignore)
.dockerignore
$(basename "$0")
EOF

docker="docker"
if command -v "podman" &> /dev/null; then
  echo "use podman"
  docker="podman"
fi

echo "build ..."
cat <<EOF | $docker build --tag "$tag" -f - .
FROM nixos/nix

RUN set -x \
 && nix-channel --add https://nixos.org/channels/nixos-unstable nixpkgs \
 && nix-channel --update

WORKDIR /ldbcollector
ADD . .
RUN nix \
    --extra-experimental-features nix-command \
    --extra-experimental-features flakes \
    profile install ".#ldbcollector-untested"
CMD ldbcollector-exe
EOF
echo "run ..."

set -x
exec $docker run --env PORT=3001 --net host "$tag"