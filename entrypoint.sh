#!/bin/bash
# SPDX-FileCopyrightText: 2024 Kaushlendra Pratap <kaushlendra-pratap.singh@siemens.com>
# SPDX-License-Identifier: GPL-2.0-only

set -e

db_host="${DB_HOST:-localhost}"
db_port="${DB_PORT:-5432}"
db_name="${DB_NAME:-fossology}"
db_user="${DB_USER:-fossy}"
db_password="${DB_PASSWORD:-fossy}"
populate_db="${POPULATE_DB:-true}"
data_file="/app/licenseRef.json"

printf "TOKEN_HOUR_LIFESPAN=24\nAPI_SECRET=%s\n" $(openssl rand -hex 32) > /app/.env

/app/laas -host=$db_host -port=$db_port -user=$db_user -dbname=$db_name \
  -password=$db_password -datafile="$data_file" -populatedb=$populate_db

