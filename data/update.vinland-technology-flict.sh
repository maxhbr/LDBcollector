#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code vinland-technology-flict; then
  git remote add -f vinland-technology-flict https://github.com/vinland-technology/flict
else
  git fetch "https://github.com/vinland-technology/flict"
fi
git subtree pull --prefix data/vinland-technology-flict vinland-technology-flict main
