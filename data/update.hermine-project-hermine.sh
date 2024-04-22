#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code hermine-project-hermine; then
  git remote add -f hermine-project-hermine https://gitlab.com/hermine-project/hermine.git
else
  git fetch "https://gitlab.com/hermine-project/hermine.git"
fi
git subtree pull --prefix data/hermine-project-hermine hermine-project-hermine main
