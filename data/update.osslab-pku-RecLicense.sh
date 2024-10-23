#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code osslab-pku-RecLicense; then
  git remote add -f osslab-pku-RecLicense https://github.com/osslab-pku/RecLicense
else
  git fetch "https://github.com/osslab-pku/RecLicense"
fi
git subtree pull --prefix data/osslab-pku-RecLicense osslab-pku-RecLicense master
