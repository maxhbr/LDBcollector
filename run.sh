#!/usr/bin/env nix-shell
#! nix-shell -i bash -p glibcLocales
set -e

cd "$(dirname "$0")"


PUSH=false
if [[ "$1" == "--push" ]]; then
    PUSH=true
    shift
fi

out="$(pwd)/_generated"
tmpdir="$(mktemp -d)"
if [[ -d "$out/.git" ]]; then
    mv "$out/.git" "$tmpdir/.git"
fi

stack build && stack exec LDBcollector-exe $@ || true

if [[ -d "$out" ]]; then
    cd "$out"
    if [[ -d "$tmpdir/.git" ]]; then
        cp ../data/OSLC-handbook/LICENSE ./ || true
        mv "$tmpdir/.git" ./
    else
        git init
        cp ../data/OSLC-handbook/LICENSE ./
        git add LICENSE
        git commit -m "Add License file with CC-By-Sa 4.0"
    fi

    git add .
    git commit -m "Commit generated output" || true

    if [[ "$PUSH" == "true" ]]; then
        git push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
    fi
else
    echo "undo git move ..."
    mkdir -p "$out"
    mv "$tmpdir/.git" "$out"
fi
