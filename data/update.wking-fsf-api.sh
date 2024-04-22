#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code wking-fsf-api; then
  git remote add -f wking-fsf-api https://github.com/wking/fsf-api
else
  git fetch "https://github.com/wking/fsf-api"
fi
git subtree pull --prefix data/wking-fsf-api wking-fsf-api gh-pages
