#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code google-licensecheck; then
  git remote add -f google-licensecheck https://github.com/google/licensecheck
else
  git fetch "https://github.com/google/licensecheck"
fi
git subtree pull --prefix data/google-licensecheck google-licensecheck main
