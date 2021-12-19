#!/usr/bin/env bash

set -ex

prefix="data/metaeffekt-universe"
cd "$(dirname "$0")/.."

if [[ ! -d "$prefix" ]] ; then
    git subtree add \
        --prefix $prefix \
        https://github.com/org-metaeffekt/metaeffekt-universe \
        main \
        --squash
else
    git subtree pull \
        --prefix $prefix \
        https://github.com/org-metaeffekt/metaeffekt-universe \
        main \
        --squash
fi
