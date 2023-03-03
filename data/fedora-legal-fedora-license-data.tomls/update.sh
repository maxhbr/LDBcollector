#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

data=../fedora-legal-fedora-license-data/data/
find "$data" -iname '*.toml' -print0 |
    while IFS= read -r -d '' toml; do
        json="$(basename "$toml").json"
        echo ".. $toml -> $json"
        tomlq . "$toml" > "$json"
    done