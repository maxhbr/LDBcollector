#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code spdx-license-list-data; then
  git remote add -f spdx-license-list-data https://github.com/spdx/license-list-data
else
  git fetch "https://github.com/spdx/license-list-data"
fi
git subtree pull --prefix data/spdx-license-list-data spdx-license-list-data main
