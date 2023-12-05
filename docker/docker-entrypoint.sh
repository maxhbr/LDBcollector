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
  f_log "create superuser if none exists with $SUPERUSER"
  python ./manage.py createsuperuser_if_none_exists --user="$SUPERUSER" --password="$PASSWORD"
fi
python -m gunicorn --workers=$NB_WORKERS --threads=$NB_THREADS --worker-class=gthread --worker-tmp-dir /dev/shm hermine.wsgi -b 0.0.0.0:"$DJANGO_PORT" -t 120
