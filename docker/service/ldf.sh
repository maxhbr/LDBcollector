#!/bin/sh

cd /srv/licensedb

exec /usr/local/bin/iojs node_modules/.bin/ldf-server etc/ldf-server.json 3000 4


