#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code openSUSE-cavil; then
  git remote add -f openSUSE-cavil https://github.com/openSUSE/cavil
else
  git fetch "https://github.com/openSUSE/cavil"
fi
git subtree pull --prefix data/openSUSE-cavil openSUSE-cavil master
