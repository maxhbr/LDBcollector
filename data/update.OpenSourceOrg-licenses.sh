#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git ls-remote --exit-code OpenSourceOrg-licenses; then
  git remote add -f OpenSourceOrg-licenses https://github.com/OpenSourceOrg/licenses
else
  git fetch "https://github.com/OpenSourceOrg/licenses"
fi
git subtree pull --prefix data/OpenSourceOrg-licenses OpenSourceOrg-licenses master

update_json() (
  # Create and setup virtual environment
  VENV_DIR="data/OpenSourceOrg-licenses.venv"
  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
  fi

  # Activate venv and install dependencies
  source "$VENV_DIR/bin/activate"
  pip install -q --upgrade pip
  pip install -q -r data/OpenSourceOrg-licenses/requirements.txt

  # Run compile.py script
  cd data/OpenSourceOrg-licenses
  python compile.py ./licenses ../OpenSourceOrg-licenses.json
  cd ../..

  # Deactivate venv
  deactivate
)

update_json