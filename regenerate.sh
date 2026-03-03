#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

OUTPUT_DIR="_generatedV2"
OUTPUT_BRANCH="generatedV2"

repo_root="$(git rev-parse --show-toplevel)"
output_dir_abs="$repo_root/$OUTPUT_DIR"

ensure_output_worktree() {
    local found_path=0
    local found_branch=0
    local current_worktree=""
    local current_branch=""

    while IFS= read -r line; do
        case "$line" in
            "worktree "*)
                current_worktree="${line#worktree }"
                current_branch=""
                ;;
            "branch "*)
                current_branch="${line#branch }"
                ;;
            "")
                if [[ "$current_worktree" == "$output_dir_abs" ]]; then
                    found_path=1
                    if [[ "$current_branch" == "refs/heads/$OUTPUT_BRANCH" ]]; then
                        found_branch=1
                    fi
                fi
                current_worktree=""
                current_branch=""
                ;;
        esac
    done < <(git -C "$repo_root" worktree list --porcelain; echo)

    if [[ "$found_path" -ne 1 ]]; then
        if [[ -e "$OUTPUT_DIR" ]]; then
            echo "ERROR: '$OUTPUT_DIR' exists but is not a configured git worktree."
            echo "Remove or rename it, then rerun this script."
            exit 1
        fi
        echo "Creating worktree '$OUTPUT_DIR' for branch '$OUTPUT_BRANCH' ..."
        git -C "$repo_root" worktree add "$OUTPUT_DIR" "$OUTPUT_BRANCH"
        found_path=1
        found_branch=1
    fi

    if [[ "$found_branch" -ne 1 ]]; then
        echo "ERROR: '$OUTPUT_DIR' is not attached to branch '$OUTPUT_BRANCH'."
        echo "Fix it by recreating the worktree on the correct branch."
        exit 1
    fi
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat <<EOF
usage:
  $0

Regenerate the output in $OUTPUT_DIR.
Requires '$OUTPUT_DIR' to be a git worktree for branch '$OUTPUT_BRANCH'.

Set CLEAN=1 to clean the output worktree before regenerating.
EOF
    exit 0
fi

ensure_output_worktree

if [[ "${CLEAN:-}" == "1" ]]; then
    echo "Cleaning worktree '$OUTPUT_DIR' ..."
    git -C "$OUTPUT_DIR" reset --hard HEAD
    git -C "$OUTPUT_DIR" clean -fdx
fi

echo "Regenerating '$OUTPUT_DIR' ..."
./nix-run.sh default --output-dir "$OUTPUT_DIR"

echo "Done. Output written to '$OUTPUT_DIR'."
