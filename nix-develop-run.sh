#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec nix develop --command cabal run
