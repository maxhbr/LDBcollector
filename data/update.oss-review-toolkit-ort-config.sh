#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code oss-review-toolkit-ort-config; then
  git remote add -f oss-review-toolkit-ort-config https://github.com/oss-review-toolkit/ort-config
else
  git fetch "https://github.com/oss-review-toolkit/ort-config"
fi
git subtree pull --prefix data/oss-review-toolkit-ort-config oss-review-toolkit-ort-config main
