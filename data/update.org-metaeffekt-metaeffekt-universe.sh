#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code org-metaeffekt-metaeffekt-universe; then
  git remote add -f org-metaeffekt-metaeffekt-universe https://github.com/org-metaeffekt/metaeffekt-universe
else
  git fetch "https://github.com/org-metaeffekt/metaeffekt-universe"
fi
git subtree pull --prefix data/org-metaeffekt-metaeffekt-universe org-metaeffekt-metaeffekt-universe main
