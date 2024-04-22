#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code warpr-licensedb; then
  git remote add -f warpr-licensedb https://github.com/warpr/licensedb
else
  git fetch "https://github.com/warpr/licensedb"
fi
git subtree pull --prefix data/warpr-licensedb warpr-licensedb master
