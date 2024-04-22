#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code github-choosealicense.com; then
  git remote add -f github-choosealicense.com https://github.com/github/choosealicense.com/
else
  git fetch "https://github.com/github/choosealicense.com/"
fi
git subtree pull --prefix data/github-choosealicense.com github-choosealicense.com gh-pages
