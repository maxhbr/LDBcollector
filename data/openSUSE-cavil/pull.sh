#!/usr/bin/env bash

tmpdir=$(mktemp -d)
trap 'rm -rf $tmpdir' EXIT
git clone https://github.com/openSUSE/cavil "$tmpdir"
cp "$tmpdir/COPYING" ./
cp -r "$tmpdir/lib/Cavil/resources/"* ./
sed -i '/"/d' ./license_changes.txt
