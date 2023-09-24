#!/usr/bin/env nix-shell
#! nix-shell -i bash -p ormolu

# SPDX-FileCopyrightText: Maximilian Huber <oss@maximilian-huber.de>
#
# SPDX-License-Identifier: MIT

set -euo pipefail

ormolu --mode inplace $(git ls-files '*.hs')

