#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code AmadeusITGroup-oscad2; then
  git remote add -f AmadeusITGroup-oscad2 https://github.com/AmadeusITGroup/oscad2/
else
  git fetch "https://github.com/AmadeusITGroup/oscad2/"
fi
git subtree pull --prefix data/AmadeusITGroup-oscad2 AmadeusITGroup-oscad2 master
