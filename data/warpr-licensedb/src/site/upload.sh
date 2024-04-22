#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd $DIR/../../www

rsync --checksum --progress --verbose --archive --delete-after * licensedb.org:/var/www/licensedb.org/

