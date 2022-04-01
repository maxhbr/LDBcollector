#!/bin/sh
# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

f_log() {
    echo "== $(date) == $@"
}

PORT=$1
if [ -z "$1" ]
then
  PORT=8080
fi

f_log "Entrypoint start on $PORT"

python ./manage.py migrate
python ./manage.py runserver 0.0.0.0:$PORT
