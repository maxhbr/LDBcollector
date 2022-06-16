#!/bin/sh
# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

# Default values
PORT=8080
USER=''
PASSWORD=''

f_log() {
    echo "== $(date) == $*"
}

f_readArgs() {
  for arg in "$@"
  do
      case $arg in
          --port=*)
            PORT="${arg#*=}"
            shift
          ;;
          -u=*|--user=*)
            USER="${arg#*=}"
            shift
          ;;
          -p=*|--password=*)
            PASSWORD="${arg#*=}"
            shift
          ;;
      esac
  done
}

f_log "enter with $*"
f_readArgs "$@"

f_log "Entrypoint start on $PORT"
python ./manage.py migrate
if test -n "$USER" && test -n "$PASSWORD"
then
  f_log "create superuser if none exists with $USER"
  python ./manage.py createsuperuser_if_none_exists --user="$USER" --password="$PASSWORD"
fi
python ./manage.py runserver 0.0.0.0:$PORT
