#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code okfn-licenses; then
  git remote add -f okfn-licenses https://github.com/okfn/licenses
else
  git fetch "https://github.com/okfn/licenses"
fi
git subtree pull --prefix data/okfn-licenses okfn-licenses master
