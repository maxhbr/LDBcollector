#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code OpenSourceOrg-licenses; then
  git remote add -f OpenSourceOrg-licenses https://github.com/OpenSourceOrg/licenses
else
  git fetch "https://github.com/OpenSourceOrg/licenses"
fi
git subtree pull --prefix data/OpenSourceOrg-licenses OpenSourceOrg-licenses master
