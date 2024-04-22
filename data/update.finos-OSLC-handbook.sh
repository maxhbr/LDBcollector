#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code finos-OSLC-handbook; then
  git remote add -f finos-OSLC-handbook https://github.com/finos/OSLC-handbook
else
  git fetch "https://github.com/finos/OSLC-handbook"
fi
git subtree pull --prefix data/finos-OSLC-handbook finos-OSLC-handbook master
