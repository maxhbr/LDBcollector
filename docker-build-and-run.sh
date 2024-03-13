#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"


docker="docker"
if command -v "podman" &> /dev/null; then
  echo "use podman"
  docker="podman"
fi
tag="maxhbr/ldbcollector"

dockerignore() {
    cat <<EOF
$(cat .gitignore)
.dockerignore
$(basename "$0")
EOF
}
 
dockerfile() {
    cat <<EOF
FROM nixos/nix
LABEL org.opencontainers.image.source="https://github.com/maxhbr/ldbcollector"

RUN set -x \
 && nix-channel --add https://nixos.org/channels/nixos-unstable nixpkgs \
 && nix-channel --update

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8     

WORKDIR /ldbcollector
ADD . .
RUN nix \
    --extra-experimental-features nix-command \
    --extra-experimental-features flakes \
    profile install --impure \
    ".#ldbcollector-untested"
CMD ldbcollector-exe
EOF
}

build() {
    echo "build ..."
    dockerignore >.dockerignore
    dockerfile | $docker build --tag "$tag" -f - .
}

run() {
    echo "run ..."
    set -x
    exec $docker run -p 3001:3001 --env PORT=3001 "$tag"
}

if [[ $# -gt 0 && "$1" == "--gen-dockerfile-only" ]]; then
    # used in CI, to build with github actions
    dockerignore >.dockerignore
    dockerfile >Dockerfile
    exit 0
fi

build
if [[ $# -gt 0 && "$1" == "--build-only" ]]; then
    exit 0
fi
run