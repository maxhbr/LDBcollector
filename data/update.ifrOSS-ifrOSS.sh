#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code ifrOSS-ifrOSS; then
  git remote add -f ifrOSS-ifrOSS https://github.com/ifrOSS/ifrOSS
else
  git fetch "https://github.com/ifrOSS/ifrOSS"
fi
git subtree pull --prefix data/ifrOSS-ifrOSS ifrOSS-ifrOSS master
