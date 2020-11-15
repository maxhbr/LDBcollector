#!/usr/bin/env bash

set -ex

target="$(dirname "$0")/nexB_scancode-toolkit_license_list"
tmp=$(mktemp -d)

git clone https://github.com/nexB/scancode-toolkit/ "$tmp"
mv "$target" "${target}.bac"
mv "$tmp/src/licensedcode/data/licenses/" "$target"
rm -rf "$tmp" "${target}.bac"
