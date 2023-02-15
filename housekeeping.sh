#!/usr/bin/env nix-shell
#! nix-shell -i bash -p crate2nix

set -euo pipefail

cd "$(dirname "$0")"

echo "#########################################################################"
echo "## formatting"
find . -iname '*.rs' -print -exec rustfmt {} \;

echo "#########################################################################"
echo "## crate2nix"
crate2nix generate

echo "#########################################################################"
echo "## cargo test"
cargo test

echo "#########################################################################"
echo "## nix build"
nix build