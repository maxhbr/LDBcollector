#!/usr/bin/env bash
set -euo pipefail

cd "$( dirname "${BASH_SOURCE[0]}" )"

entr_task() (
  set -ex
  stack run
)
export -f entr_task

while sleep 1; do
  cat <<EOF | entr -dr bash -c entr_task
$0
$(find src)
$(find test)
$(find app)
package.yaml
stack.yaml
shell.nix
EOF
done
