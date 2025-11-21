#!/bin/sh

f_log() {
    echo "== $(date) == $*"
}

f_log "Entrypoint start on $DJANGO_PORT"
python ./manage.py migrate

if [ -f /opt/hermine/shared.json ]
then
  python ./manage.py init_shared_data /opt/hermine/shared.json
fi

if test -n "$SUPERUSER" && test -n "$PASSWORD"
then
  f_log "create superuser if none exists with $SUPERUSER"
  python ./manage.py createsuperuser_if_none_exists --user="$SUPERUSER" --password="$PASSWORD"
fi
python -m gunicorn --workers=2 --threads=${DJANGO_THREADS:-$(nproc --all)} --worker-class=gthread --worker-tmp-dir /dev/shm hermine.wsgi -b 0.0.0.0:"$DJANGO_PORT" -t 120
