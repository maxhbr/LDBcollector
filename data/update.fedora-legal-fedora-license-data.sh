#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code fedora-legal-fedora-license-data; then
  git remote add -f fedora-legal-fedora-license-data https://gitlab.com/fedora/legal/fedora-license-data
else
  git fetch "https://gitlab.com/fedora/legal/fedora-license-data"
fi
git subtree pull --prefix data/fedora-legal-fedora-license-data fedora-legal-fedora-license-data main
