#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd $DIR/../site

cat src/top.txt src/ns.html src/bottom.txt > publish/ns
cat src/top.txt src/about.html src/bottom.txt > publish/about
cat src/top.txt src/index.html src/bottom.txt > publish/index.html




