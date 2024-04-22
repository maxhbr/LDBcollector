#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code oslic; then
  git remote add -f oslic https://github.com/telekom/oslic
else
  git fetch "https://github.com/telekom/oslic"
fi
git subtree pull --prefix data/oslic oslic master
