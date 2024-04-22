#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code HansHammel-license-compatibility-checker; then
  git remote add -f HansHammel-license-compatibility-checker https://github.com/HansHammel/license-compatibility-checker
else
  git fetch "https://github.com/HansHammel/license-compatibility-checker"
fi
git subtree pull --prefix data/HansHammel-license-compatibility-checker HansHammel-license-compatibility-checker master
