#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ "$#" -eq 1 && "$1" == "--help" ]]; then
    cat <<EOF
usage:
  $0

This
 - runs the server using nix
EOF
    exit 0
fi

exec nix run ".#" -- "$@"
