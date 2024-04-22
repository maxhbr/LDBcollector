#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code McCoySmith-OSI-License-Categories; then
  git remote add -f McCoySmith-OSI-License-Categories https://github.com/McCoySmith/OSI-License-Categories
else
  git fetch "https://github.com/McCoySmith/OSI-License-Categories"
fi
git subtree pull --prefix data/McCoySmith-OSI-License-Categories McCoySmith-OSI-License-Categories main
