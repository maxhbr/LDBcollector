#!/usr/bin/env bash
set -euo pipefail
mkdir -p librariesio-license-compatibility
curl https://raw.githubusercontent.com/librariesio/license-compatibility/master/lib/license/licenses.json > librariesio-license-compatibility/licenses.json
curl https://raw.githubusercontent.com/librariesio/license-compatibility/master/LICENSE > librariesio-license-compatibility/LICENSE
