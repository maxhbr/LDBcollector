#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code google-licenseclassifier; then
  git remote add -f google-licenseclassifier https://github.com/google/licenseclassifier
else
  git fetch "https://github.com/google/licenseclassifier"
fi
git subtree pull --prefix data/google-licenseclassifier google-licenseclassifier main
