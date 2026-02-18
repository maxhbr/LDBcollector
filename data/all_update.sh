#!/usr/bin/env bash

set -uo pipefail

if git diff --quiet; then
    echo "Working tree has modifications. Please commit or stash your changes before running this script."
    exit 1
fi

failed_scripts=()

# Find and execute all update.*.sh scripts
while IFS= read -r script; do
    echo "Running: $script"
    if ! "$script"; then
        failed_scripts+=("$script")
    fi
    
    # if git diff --quiet; then
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
