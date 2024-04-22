#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code librariesio-license-compatibility; then
  git remote add -f librariesio-license-compatibility https://github.com/librariesio/license-compatibility
else
  git fetch "https://github.com/librariesio/license-compatibility"
fi
git subtree pull --prefix data/librariesio-license-compatibility librariesio-license-compatibility master
