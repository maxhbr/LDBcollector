#!/usr/bin/env nix-shell
#! nix-shell -i bash -p haskellPackages.stylish-haskell

# SPDX-FileCopyrightText: Maximilian Huber <oss@maximilian-huber.de>
#
# SPDX-License-Identifier: MIT

set -euo pipefail

formatDir() {
    # formatters:
    # * hindent
    # * stylish-haskell
    # * brittany <- breaks GADTs
    find "$(dirname "$0")/$1" -iname '*.hs' -print -exec stylish-haskell --inplace {} \;
}

formatDir src
formatDir test
formatDir app

