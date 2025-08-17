#!/bin/bash
# Terminate existing connections
echo "Terminating existing connections to 'poster_judging'..."
psql -U $(whoami) -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'poster_judging' AND pid <> pg_backend_pid();
"

# Drop the database
echo "Dropping existing database 'poster_judging'..."
psql -U $(whoami) -d postgres -c "DROP DATABASE IF EXISTS poster_judging;"

# Recreate database and roles
echo "Creating roles and database..."
psql -U $(whoami) -d postgres -f 1_create_roles_and_db.sql

# Check if database exists
if ! psql -U $(whoami) -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='poster_judging'" | grep -q 1; then
    createdb -U $(whoami) -O admin poster_judging
    echo "Database 'poster_judging' created."
else
    echo "Database 'poster_judging' already exists."
fi

psql -U $(whoami) -d postgres -c "GRANT CONNECT ON DATABASE poster_judging TO app_user;"

psql -U $(whoami) -d poster_judging -f 2_grant_permissions.sql
psql -U $(whoami) -d poster_judging -f 3_create_tables.sql
psql -U $(whoami) -d poster_judging -f 4_sample_data.sql

