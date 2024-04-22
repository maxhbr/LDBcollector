#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code hermine-project-hermine-data; then
  git remote add -f hermine-project-hermine-data https://gitlab.com/hermine-project/community-data
else
  git fetch "https://gitlab.com/hermine-project/community-data"
fi
git subtree pull --prefix data/hermine-project-hermine-data hermine-project-hermine-data main
