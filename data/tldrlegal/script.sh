#!/usr/bin/env nix-shell
#! nix-shell -i bash -p curl jq
# Copyright 2019 Maximilian Huber <oss@maximilian-huber.de>
# SPDX-License-Identifier: MIT

set -e

getLicensePage() {
    local page=$1
    curl "https://tldrlegal.com/api/license/?page=$page"
}

getLicenseDetails() {
    local id=$1
    curl "https://tldrlegal.com/api/license/$id"
}

getAttributePage() {
    local page=$1
    curl "https://tldrlegal.com/api/attributes/?page=$page"
}

getAttributeDetails() {
    local id=$1
    curl "https://tldrlegal.com/api/attributes/$id"
}

header='Type,"Obligation or Risk topic","Full Text",Classification,"Apply on modified source code",Comment,"Associated Licenses","Associated candidate Licenses"'

if [[ ! -d "license" ]]; then
    mkdir -p license
    for i in $(seq 0 43); do
        getLicensePage $i > "license/page_$i.json"
    done
fi
for json in license/*.json; do
    for row64 in $(cat $json | jq -r '.[] | @base64'); do
        row=$(echo ${row64} | base64 --decode)
        if [[ "$(echo $row | jq -r '.type.name')" == "Code License" ]]; then
            id=$(echo $row | jq -r '._id')
            title=$(echo $row | jq -r '.title')
            shorthand=$(echo $row | jq -r '.shorthand')

            rawSpdxId="${title##* }"
            spdxId=""
            if [[ "$rawSpdxId" =~ \(.*\) ]]; then
                rawSpdxId="${rawSpdxId:1}"
                spdxId="${rawSpdxId::-1}"
            fi

            outDir="license/$id"
            if [[ ! -d $outDir ]]; then
                mkdir -p "$outDir"
                echo $row | jq -r '.slug' > "$outDir/slug.txt"
                echo $title > "$outDir/title.txt"
                echo $shorthand > "$outDir/shorthand.txt"
                echo $id > "$outDir/id.txt"
                echo $spdxId > "$outDir/spdxId.txt"
                getLicenseDetails $id > "$outDir/json"
            fi

            if [[ $spdxId ]]; then
                echo "$spdxId: $title"
                array=( must can cannot )
                for kind in "${array[@]}"; do
                    echo "   $kind:"
                    for must64 in $(cat "$outDir/json" | jq -r '.modules.summary.'$kind'[] | [.attribute.title, .attribute._id] | @base64'); do
                        must=$(echo $must64 | base64 --decode)
                        mustTitle=$(echo $must | jq -r '.[0]')
                        mustId=$(echo $must | jq -r '.[1]')
                        echo "      $mustTitle"

                        mustOutDir="attribute/$mustId/$kind/"
                        mkdir -p "$mustOutDir"
                        echo $spdxId > "$mustOutDir/$id"
                        if [[ "x$shorthand" != "x" && "$shorthand" != "null" && "$shorthand" != "$spdxId" ]]; then
                            echo $shorthand >> "$mustOutDir/$id"
                            echo $shorthand | awk '{ print toupper($0) }' >> "$mustOutDir/$id"
                        fi
                    done
                done
            fi
        fi
    done
done

echo "$header" | tee tldrObligations.csv
if [[ ! -f "attribute/page_0.json" ]]; then
    mkdir -p attribute
    for i in $(seq 0 2); do
        getAttributePage $i > "attribute/page_$i.json"
    done
fi
for json in attribute/*.json; do
    for row64 in $(cat $json | jq -r '.[] | @base64'); do
        row=$(echo ${row64} | base64 --decode)
        id=$(echo $row | jq -r '._id')
        outDir="attribute/$id"
        if [[ ! -f "$outDir/json" ]]; then
            mkdir -p "$outDir"
            getAttributeDetails $id > "$outDir/json"
        fi

        detailJson=$(cat "$outDir/json")
        if [[ -d "$outDir/must" ]]; then
            files=("$outDir/must/"*)
            if [ ${#files[@]} -gt 0 ]; then
                title=$(echo $detailJson | jq -r '.title')
                description=$(echo $detailJson | jq -r '.description' | sed -r 's/"/\\"/g' )
                ids=$(cat "$outDir/must/"* | tr '\n' ';')
                ids="${ids::-1}"
                if [[ ! "x$ids" == "x" ]]; then
                    echo -e "Obligation,\"$title\",\"You must: $title\",white,Yes,\"\",$ids," | tee -a tldrObligations.csv
                fi
            fi
         fi
        if [[ -d "$outDir/can" ]]; then
            files=("$outDir/can/"*)
            if [ ${#files[@]} -gt 0 ]; then
                title=$(echo $detailJson | jq -r '.title')
                description=$(echo $detailJson | jq -r '.description' | sed -r 's/"/\\"/g' )
                ids=$(cat "$outDir/can/"* | tr '\n' ';')
                ids="${ids::-1}"
                if [[ ! "x$ids" == "x" ]]; then
                    echo -e "Right,\"$title\",\"You can: $title\",white,Yes,\"\",$ids," | tee -a tldrObligations.csv
                fi
            fi
        fi
        if [[ -d "$outDir/cannot" ]]; then
            files=("$outDir/cannot/"*)
            if [ ${#files[@]} -gt 0 ]; then
                title=$(echo $detailJson | jq -r '.title')
                description=$(echo $detailJson | jq -r '.description' | sed -r 's/"/\\"/g' )
                ids=$(cat "$outDir/cannot/"* | tr '\n' ';')
                ids="${ids::-1}"
                if [[ ! "x$ids" == "x" ]]; then
                    echo -e "Restriction,\"$title\",\"You cannot: $title\",white,Yes,\"\",$ids," | tee -a tldrObligations.csv
                fi
            fi
        fi
    done
done


