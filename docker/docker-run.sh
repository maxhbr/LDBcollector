#!/usr/bin/env bash

set -euo pipefail

podman run --env PORT=3001 --net host maxhbr/ldbcollector