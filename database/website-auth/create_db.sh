#!/bin/bash
DATABASE='poster_judging_db'
APP_USER='app_user'
ADMIN_USER='admin'   # assuming you have an admin role that owns the DB

# Terminate existing connections
echo "Terminating existing connections to '${DATABASE}'..."
psql -U $(whoami) -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DATABASE}' AND pid <> pg_backend_pid();
"

# Drop the database
echo "Dropping existing database '${DATABASE}'..."
psql -U $(whoami) -d postgres -c "DROP DATABASE IF EXISTS ${DATABASE};"

# Recreate roles and database
echo "Creating roles and database..."
psql -U $(whoami) -d postgres -v db=${DATABASE} -v app_user=${APP_USER} -f 1_create_roles_and_db.sql

# Check if database exists
if ! psql -U $(whoami) -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DATABASE}'" | grep -q 1; then
    createdb -U $(whoami) -O ${ADMIN_USER} ${DATABASE}
    echo "Database '${DATABASE}' created."
else
    echo "Database '${DATABASE}' already exists."
fi

# Grant DB connect to app user
psql -U $(whoami) -d postgres -c "GRANT CONNECT ON DATABASE ${DATABASE} TO ${APP_USER};"

# Run schema and data scripts
psql -U $(whoami) -d ${DATABASE} -f 2_grant_permissions.sql -v app_user=${APP_USER}
psql -U $(whoami) -d ${DATABASE} -f 3_create_tables.sql
psql -U $(whoami) -d ${DATABASE} -f 4_sample_data.sql

