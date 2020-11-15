#!/usr/bin/env bash

set -ex

target="$(dirname "$0")/OSLC-handbook"
tmp=$(mktemp -d)

git clone https://github.com/finos/OSLC-handbook "$tmp"
mv "$target" "${target}.bac"
mv "$tmp/src/" "$target"
mv "$tmp/LICENSE" "$target"
rm -rf "$tmp" "${target}.bac"
