#!/usr/bin/env bash

{
    echo '"_id","shorthand","slug","title"'
    find license/ \
        -name 'json' \
        -exec jq -r '. | [._id,.shorthand,.slug,.title]|@csv' {} \;
} > tldrLicenses.csv
