#!/usr/bin/env nix-shell
#! nix-shell -i bash -p jq
set -ex

stack exec LDBcollector-exe

cd _generated
git init
git add .
git commit -m "Commit generated output"
mkdir -p formatted
find . -iname '*.json' -type f -print0 | while IFS= read -d '' -r file; do
    cat $file | jq > "formatted/$file"
done
git add .
git commit -m "Commit formatted output"
git push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
