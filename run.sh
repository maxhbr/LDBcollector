#!/usr/bin/env nix-shell
#! nix-shell -i bash -p glibcLocales
set -e

cd "$(dirname "$0")"

stack build
if [[ "$1" == "--test" ]]; then
    shift
    yml=$(readlink -f stack.yaml)
    set -x
    cd "$(mktemp -d)"
    stack --stack-yaml "$yml" \
        exec LDBcollector-exe $@
    pwd
else
    PUSH=false
    if [[ "$1" == "--push" ]]; then
        PUSH=true
        shift
    fi

    out="$(pwd)/_generated"
    outGit="${out}.git"

    set -x
    stack exec LDBcollector-exe $@

    if [[ -d "$out" ]]; then
        cd "$out"
        if [[ ! -f "LICENSE" ]]; then
            cp ../data/OSLC-handbook/LICENSE ./
        fi
        if [[ ! -d "$outGit" ]]; then
            git init --separate-git-dir="$outGit" .
            git --git-dir="$outGit" add LICENSE
            git --git-dir="$outGit" commit -m "Add License file with CC-By-Sa 4.0"
        fi

        git --git-dir="$outGit" add .
        git --git-dir="$outGit" commit -m "Commit generated output" || true

        if [[ "$PUSH" == "true" ]]; then
            git --git-dir="$outGit" push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
        fi
    fi
fi
