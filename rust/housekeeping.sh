#!/usr/bin/env nix-shell
#! nix-shell -i bash -p crate2nix

set -euo pipefail

cd "$(dirname "$0")"

echo "#########################################################################"
echo "## formatting"
fmt() {
    find "$1" -iname '*.rs' -print -exec rustfmt --edition 2021 {} \;
}
fmt src
fmt tests

echo "#########################################################################"
echo "## crate2nix"
crate2nix generate

echo "#########################################################################"
echo "## cargo test"
cargo test
