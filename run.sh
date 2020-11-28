#!/usr/bin/env nix-shell
#! nix-shell -i bash -p glibcLocales
set -e

cd "$(dirname "$0")"

stack build --ghc-options -j
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
    PRIV=false
    out="$(pwd)/_generated"
    if [[ "$1" == "--priv" ]]; then
        PRIV=true
        PUSH=false
        out="$(pwd)/_generated.priv"
        shift
    fi
    outGit="${out}.git"

    set -x
    stack exec LDBcollector-exe $@ "$($PRIV && echo "priv")"

    if [[ -d "$out" ]]; then
        cd "$out"
        if [[ ! -d "$outGit" ]]; then
            touch README
            git init --separate-git-dir="$outGit" .
            git --git-dir="$outGit" add README
            git --git-dir="$outGit" commit -m "initial commit"
        fi

        git --git-dir="$outGit" add .
        git --git-dir="$outGit" commit -m "Commit generated output" || true

        if [[ "$PUSH" == "true" ]]; then
            git --git-dir="$outGit" push --force "https://github.com/maxhbr/LDBcollector.git" master:generated
        fi
    fi
fi
