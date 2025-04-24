#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code licenselynx-licenselynx; then
  git remote add -f licenselynx-licenselynx https://github.com/licenselynx/licenselynx
else
  git fetch "https://github.com/licenselynx/licenselynx"
fi
git subtree pull --prefix data/licenselynx-licenselynx licenselynx-licenselynx main
