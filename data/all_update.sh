#!/usr/bin/env bash

set -uo pipefail

failed_scripts=()

# Find and execute all update.*.sh scripts
while IFS= read -r script; do
    echo "Running: $script"
    if ! "$script"; then
        failed_scripts+=("$script")
    fi
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
