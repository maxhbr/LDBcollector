#!/bin/bash

echo === creating not-a-repo ===
mkdir not-a-repo

echo === creating empty ===
mkdir empty
createrepo empty

echo === creating testmodule ===
mkdir testmodule
for rpm in perl-List-Compare perl-Tangerine tangerine
do
  dnf download --destdir testmodule $rpm
done
createrepo testmodule
