#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code Hitachi-open-license; then
  git remote add -f Hitachi-open-license https://github.com/Hitachi/open-license
else
  git fetch "https://github.com/Hitachi/open-license"
fi
git subtree pull --prefix data/Hitachi-open-license Hitachi-open-license master
