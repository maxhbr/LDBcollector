#!/bin/sh
# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

f_log() {
    echo "== $(date) == $@"
}

f_log "Entrypoint start"

python ./manage.py migrate
python ./manage.py runserver 0.0.0.0:8080
