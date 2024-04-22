#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code doubleopen-project-policy-configuration; then
  git remote add -f doubleopen-project-policy-configuration https://github.com/doubleopen-project/policy-configuration
else
  git fetch "https://github.com/doubleopen-project/policy-configuration"
fi
git subtree pull --prefix data/doubleopen-project-policy-configuration doubleopen-project-policy-configuration main
