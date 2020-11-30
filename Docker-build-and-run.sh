#!/usr/bin/env bash
set -euo pipefail

docker build -t ldbserver .
docker run -it --net=host ldbserver:latest
