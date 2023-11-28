#!/bin/sh

f_log() {
    echo "== $(date) == $*"
}

f_log "Entrypoint start on $DJANGO_PORT"
python ./manage.py migrate
python ./manage.py collectstatic --noinput --clear

if [ -f ../shared.json ]
then
  python ./manage.py init_shared_data ../shared.json
fi

if test -n "$SUPERUSER" && test -n "$PASSWORD"
then
  f_log "create superuser if none exists with $USER"
  python ./manage.py createsuperuser_if_none_exists --user="$SUPERUSER" --password="$PASSWORD"
fi
python ./manage.py runserver 0.0.0.0:"$DJANGO_PORT"
