#!/usr/bin/env bash

while sleep 1; do
  find src -iname '*.rs' | entr -dr cargo run;
done