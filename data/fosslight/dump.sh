#!/usr/bin/env nix-shell
#! nix-shell -i bash -p docker wget sqlite

set -euo pipefail

cd "$(dirname "$0")"

container="fosslight-dumper"

cleanupContainer() {
    docker rm -f $container
}

startContainer() {
    mkdir -p docker-entrypoint-initdb.d
    curl https://raw.githubusercontent.com/fosslight/fosslight/main/install/db/fosslight_create.sql > docker-entrypoint-initdb.d/fosslight_create.sql
    set -x
    cleanupContainer
    docker logs "$(docker run --rm\
        --name $container \
        -e MYSQL_ROOT_PASSWORD=my-secret-pw \
        -v "$(pwd)/docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d" \
        -v "$(pwd)/out:/out" \
        -d mariadb:latest && sleep 3)"
    sleep 60
}

dumpTable() {
    tablename="$1"

    dumpCMD="exec mysqldump "
    dumpARGS="-uroot -pmy-secret-pw"
    dumpARGS="$dumpARGS --skip-create-options"
    dumpARGS="$dumpARGS --compatible=ansi"
    dumpARGS="$dumpARGS --skip-extended-insert"
    dumpARGS="$dumpARGS --compact"
    dumpARGS="$dumpARGS --single-transaction"

    awk -f <(curl https://raw.githubusercontent.com/dumblob/mysql2sqlite/master/mysql2sqlite) <(docker exec $container sh -c "$dumpCMD fosslight $tablename $dumpARGS")
}

startContainer
rm -f fosslight.sqlite.db
cat <<EOF | tee fosslight.sqlite.db.sql | sqlite3 fosslight.sqlite.db
$(dumpTable LICENSE_MASTER)
$(dumpTable LICENSE_NICKNAME)
EOF
cleanupContainer
