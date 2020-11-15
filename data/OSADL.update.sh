#!/usr/bin/env bash

set -e

FILES=./spdx-license-list-data/details/*.json
mkdir -p OSADL
for f in $FILES; do
    echo "Processing $id file..."
    id=$(basename $f)
    id="${id%.*}"
    response=$(curl -s --connect-timeout 10 "https://www.osadl.org/fileadmin/checklists/unreflicenses/${id}.txt" || true)
    if [ -n "$response" ]; then
        if [[ $response != *"was not found on this server."* ]]; then
            echo "$response" | tee "OSADL/$id.osadl"
        fi
    fi
done
