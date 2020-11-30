#!/usr/bin/env bash
set -euo pipefail
mkdir -p HansHammel-license-compatibility-checker
curl https://raw.githubusercontent.com/HansHammel/license-compatibility-checker/master/lib/licenses.json > HansHammel-license-compatibility-checker/licenses.json
curl https://raw.githubusercontent.com/HansHammel/license-compatibility-checker/master/LICENSE > HansHammel-license-compatibility-checker/LICENSE
