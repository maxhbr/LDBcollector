#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code telekom-oslic; then
  git remote add -f telekom-oslic https://github.com/telekom/oslic
else
  git fetch "https://github.com/telekom/oslic"
fi
git subtree pull --prefix data/telekom-oslic telekom-oslic master
