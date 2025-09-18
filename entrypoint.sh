#!/bin/bash
# SPDX-FileCopyrightText: 2024-2025 Kaushlendra Pratap <kaushlendra-pratap.singh@siemens.com>
# SPDX-License-Identifier: GPL-2.0-only

set -o errexit -o nounset -o pipefail

db_host="${DB_HOST:-localhost}"
db_port="${DB_PORT:-5432}"
db_name="${DB_NAME:-licensedb}"
db_user="${DB_USER:-fossy}"
db_password="${DB_PASSWORD:-fossy}"
populate_db="${POPULATE_DB:-true}"
data_file="/app/licenseRef.json"

entry_level_user_name="fossy_super_admin"
entry_level_user_password="fossy_super_admin"
entry_level_user_display_name="fossy_super_admin"
entry_level_user_email="fossy_super_admin@example.org"

echo "API_SECRET=$(openssl rand -hex 32)" >> /app/.env

echo "Initializing PostgreSQL database..."
PGPASSWORD=$db_password psql -h "$db_host" -U "$db_user" -p "$db_port" -d "$db_name"<<EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${db_name}') THEN
      CREATE DATABASE ${db_name};
   END IF;
END
\$\$;
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${db_user}') THEN
      CREATE USER ${db_user} WITH PASSWORD '${db_password}';
   END IF;
END
\$\$;
GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO ${db_user};
ALTER DATABASE ${db_name} OWNER TO ${db_user};
EOF

echo "Database initialization done!"

echo "Running database migrations..."
migrate -path /app/pkg/db/migrations -database "postgres://$db_user:$db_password@$db_host:$db_port/$db_name?sslmode=disable" up

echo "Inserting initial SUPER_ADMIN user if not exists..."

PGPASSWORD="$db_password" psql -h "$db_host" -U "$db_user" -p "$db_port" -d "$db_name" -c \
"INSERT INTO users (user_name, user_password, user_level, display_name, user_email)
 SELECT '$entry_level_user_name', '$entry_level_user_password', 'SUPER_ADMIN', '$entry_level_user_display_name', '$entry_level_user_email'
 WHERE NOT EXISTS (SELECT 1 FROM users WHERE user_level='SUPER_ADMIN');"

echo "Starting LAAS service..."
/app/laas
