#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code nexB-scancode-licensedb; then
  git remote add -f nexB-scancode-licensedb https://github.com/nexB/scancode-licensedb
else
  git fetch "https://github.com/nexB/scancode-licensedb"
fi
git subtree pull --prefix data/nexB-scancode-licensedb nexB-scancode-licensedb main
