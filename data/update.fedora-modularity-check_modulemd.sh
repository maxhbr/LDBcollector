#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code fedora-modularity-check_modulemd; then
  git remote add -f fedora-modularity-check_modulemd https://github.com/fedora-modularity/check_modulemd
else
  git fetch "https://github.com/fedora-modularity/check_modulemd"
fi
git subtree pull --prefix data/fedora-modularity-check_modulemd fedora-modularity-check_modulemd master
