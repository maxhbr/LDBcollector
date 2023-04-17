#!/usr/bin/env bash
set -euo pipefail

cd "$( dirname "${BASH_SOURCE[0]}" )"

git submodule init
git submodule update

while sleep 1; do
  find src -iname '*.rs' | entr -dr cargo run;
done
