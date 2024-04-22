#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code ErikMcClure-bad-licenses; then
  git remote add -f ErikMcClure-bad-licenses https://github.com/ErikMcClure/bad-licenses
else
  git fetch "https://github.com/ErikMcClure/bad-licenses"
fi
git subtree pull --prefix data/ErikMcClure-bad-licenses ErikMcClure-bad-licenses master
