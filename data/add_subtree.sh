#!/usr/bin/env bash

set -euo pipefail

mname="$1"
murl="$2"
mcommit="$3"
branch="${4:-main}"
mpath="data/$mname"

cd "$(dirname "$0")/.."

# add the remote
if ! git ls-remote --exit-code $mname; then
  git remote add -f $mname $murl
else
  git fetch "$murl"
fi

git subtree add --prefix $mpath $mcommit # add the subtree

updatesh=data/update.$mname.sh
cat <<EOF > "$updatesh"
#!/usr/bin/env bash
set -euo pipefail
cd "\$(dirname "\$0")/.."
if ! git ls-remote --exit-code $mname; then
  git remote add -f $mname $murl
else
  git fetch "$murl"
fi
git subtree pull --prefix $mpath $mname $branch
EOF

git add "$updatesh"
chmod +x "$updatesh"
