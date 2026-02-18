#!/usr/bin/env bash

set -uo pipefail

if ! git diff --quiet; then
    echo "Working tree has modifications. Please commit or stash your changes before running this script."
    exit 1
fi

UPDATE_DATES_DIR="$(dirname "$0")/_update_dates"
mkdir -p "$UPDATE_DATES_DIR"

should_skip() {
    local scriptname="$1"
    local datafile="$UPDATE_DATES_DIR/${scriptname}.data"
    if [[ -f "$datafile" ]]; then
        local last_update=$(cat "$datafile")
        local current=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local diff=$(( ( $(date -d "$current" +%s) - $(date -d "$last_update" +%s) ) ))
        if [[ $diff -lt 86400 ]]; then
            return 0
        fi
    fi
    return 1
}

record_update() {
    local scriptname="$1"
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$UPDATE_DATES_DIR/${scriptname}.data"
}

failed_scripts=()

# Find and execute all update.*.sh scripts
while IFS= read -r script; do
    scriptname=$(basename "$script" .sh)
    
    if should_skip "$scriptname"; then
        echo "Skipping: $script (last update less than 1 day ago)"
        continue
    fi
    
    echo "Running: $script"
    if ! "$script"; then
        failed_scripts+=("$script")
    else
        record_update "$scriptname"
    fi
    
    # if ! git diff --quiet; then
    #     echo "Working tree has modifications. Please commit or stash your changes before running this script."
    #     exit 1
    # fi
done < <(find "$(dirname "$0")" \
    -mindepth 1 \
    -maxdepth 1 \
    -executable \
    -iname 'update.*.sh' \
    -print | sort)

# Report results
if [ ${#failed_scripts[@]} -gt 0 ]; then
    echo ""
    echo "Failed scripts:"
    for script in "${failed_scripts[@]}"; do
        echo "  - $script"
    done
    exit 1
else
    echo ""
    echo "All scripts completed successfully."
    exit 0
fi
