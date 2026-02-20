#!/usr/bin/env bash
set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to fetch GitHub Pages versions metadata"
  exit 1
fi

if ! command -v ruby >/dev/null 2>&1; then
  echo "ruby is required to parse GitHub Pages versions metadata"
  exit 1
fi

pages_ruby_version="$({
  curl -fsSL https://pages.github.com/versions.json
} | ruby -rjson -e 'print JSON.parse(STDIN.read).fetch("ruby")')"

if [[ -z "${pages_ruby_version}" ]]; then
  echo "Could not determine Ruby version from https://pages.github.com/versions.json"
  exit 1
fi

echo "GitHub Pages Ruby version: ${pages_ruby_version}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to initialize submodules"
  exit 1
fi

echo "Initializing/updating git submodules"
git submodule update --init --recursive

# RVM scripts can reference internal variables before they are initialized,
# which fails under `set -u` (for example: `_system_name: unbound variable`).
# Temporarily disable nounset while sourcing and invoking RVM.
nounset_was_set=0
if [[ $- == *u* ]]; then
  nounset_was_set=1
  set +u
fi

if [[ -s /usr/local/rvm/scripts/rvm ]]; then
  source /usr/local/rvm/scripts/rvm
elif [[ -s "$HOME/.rvm/scripts/rvm" ]]; then
  source "$HOME/.rvm/scripts/rvm"
else
  echo "RVM was not found; unable to auto-install Ruby ${pages_ruby_version}"
  exit 1
fi

rvm install "${pages_ruby_version}" --quiet-curl
rvm use "${pages_ruby_version}"
rvm alias create default "${pages_ruby_version}"

if [[ "${nounset_was_set}" -eq 1 ]]; then
  set -u
fi

gem install bundler --no-document
bundle install