#!/bin/sh

. /etc/apache2/envvars

mkdir --parents "$APACHE_LOCK_DIR"
mkdir --parents "$APACHE_RUN_DIR"

exec /usr/sbin/apache2 -DFOREGROUND
