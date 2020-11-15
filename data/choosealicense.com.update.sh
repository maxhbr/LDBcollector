#!/usr/bin/env bash

set -ex

target="$(dirname "$0")/choosealicense.com"
tmp=$(mktemp -d)

git clone https://github.com/github/choosealicense.com "$tmp"
mv "$target" "${target}.bac"
mv "$tmp/_licenses/" "$target"
mv "$tmp/LICENSE.md" "$target"
rm -rf "$tmp" "${target}.bac"
