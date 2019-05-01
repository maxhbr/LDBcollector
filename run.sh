#!/usr/bin/env nix-shell
#! nix-shell -i bash -p jq
set -e

stack exec LDBcollector-exe

if [[ -d "_generated" ]]; then
    cd _generated
    git init
    git add .
    git commit -m "Commit generated output"
    mkdir -p formatted
    find . -iname '*.json' -type f -print0 | while IFS= read -d '' -r file; do
        echo "reformat $file"
        cat "$file" | jq > "formatted/$file"
    done
    git add .
    git commit -m "Commit formatted output"

    if [[ "$1" == "--push" ]]; then
        git push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
    fi
fi
