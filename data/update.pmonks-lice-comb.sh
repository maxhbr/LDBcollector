#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code pmonks-lice-comb; then
  git remote add -f pmonks-lice-comb https://github.com/pmonks/lice-comb
else
  git fetch "https://github.com/pmonks/lice-comb"
fi
git subtree pull --prefix data/pmonks-lice-comb pmonks-lice-comb dev
