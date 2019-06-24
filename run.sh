#!/usr/bin/env nix-shell
#! nix-shell -i bash -p glibcLocales
set -e

cd "$(dirname "$0")"

stack build
stack exec LDBcollector-exe

if [[ "$1" == "--push" ]]; then
    if [[ -d "_generated" ]]; then
        cd _generated
        git init
        cp ../data/OSLC-handbook/LICENSE ./
        git add LICENSE
        git commit -m "Add License file with CC-By-Sa 4.0"
        git add .
        git commit -m "Commit generated output"

        git push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
    fi
fi
