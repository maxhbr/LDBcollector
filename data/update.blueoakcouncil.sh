#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p blueoakcouncil
curl https://blueoakcouncil.org/list.json > blueoakcouncil/blue-oak-council-license-list.json
curl https://blueoakcouncil.org/copyleft.json > blueoakcouncil/blue-oak-council-copyleft-list.json
