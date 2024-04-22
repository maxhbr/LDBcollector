#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code fossology-LicenseDb; then
  git remote add -f fossology-LicenseDb https://github.com/fossology/LicenseDb/
else
  git fetch "https://github.com/fossology/LicenseDb/"
fi
git subtree pull --prefix data/fossology-LicenseDb fossology-LicenseDb main
