#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code hesa-foss-licenses; then
  git remote add -f hesa-foss-licenses https://github.com/hesa/foss-licenses
else
  git fetch "https://github.com/hesa/foss-licenses"
fi
git subtree pull --prefix data/hesa-foss-licenses hesa-foss-licenses main
