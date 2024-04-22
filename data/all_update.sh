#!/usr/bin/env bash

set -euo pipefail
find "$(dirname "$0")" \
    -mindepth 1 \
    -maxdepth 1 \
    -executable \
    -iname 'update.*.sh' \
    -print \
    -exec {} \;
