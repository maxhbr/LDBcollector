#!/usr/bin/env bash
cd "$(dirname "$0")"
exec nix develop -c code .
