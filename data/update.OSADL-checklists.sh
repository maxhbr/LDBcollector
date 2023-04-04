#!/usr/bin/env bash

set -e

mkdir -p OSADL-checklists
cd OSADL-checklists
wget -O language.txt https://www.osadl.org/fileadmin/checklists/all/language.txt
wget -O actions.txt https://www.osadl.org/fileadmin/checklists/all/actions.txt
wget -O terms.txt https://www.osadl.org/fileadmin/checklists/all/terms.txt
wget -O unreflicenses.txt https://www.osadl.org/fileadmin/checklists/all/unreflicenses.txt
wget -O matrix.csv https://www.osadl.org/fileadmin/checklists/matrix.csv
wget -O matrix.json https://www.osadl.org/fileadmin/checklists/matrix.json
wget -O matrixseq.json https://www.osadl.org/fileadmin/checklists/matrixseq.json
wget -O matrixseqexpl.json https://www.osadl.org/fileadmin/checklists/matrixseqexpl.json
curl https://www.osadl.org/fileadmin/checklists/checklists-rawdata.tgz | tar -xz
