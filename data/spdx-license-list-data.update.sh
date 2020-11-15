#!/usr/bin/env bash

set -ex

target="$(dirname "$0")/spdx-license-list-data"
tmp=$(mktemp -d)

git clone https://github.com/spdx/license-list-data "$tmp"
mv "$target" "${target}.bac"
mv "$tmp/json" "$target"
rm -rf "$tmp" "${target}.bac"
