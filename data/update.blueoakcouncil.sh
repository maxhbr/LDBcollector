#!/usr/bin/env bash
set -euo pipefail
mkdir -p blueoakcouncil
curl https://blueoakcouncil.org/list.json > blueoakcouncil/blue-oak-council-license-list.json
curl https://blueoakcouncil.org/copyleft.json > blueoakcouncil/blue-oak-council-copyleft-list.json
