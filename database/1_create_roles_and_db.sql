-- Create an admin superuser (optional if one doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN
        CREATE ROLE admin WITH LOGIN SUPERUSER PASSWORD 'su_passw0rd';
    END IF;
END
$$ LANGUAGE plpgsql;

-- Create a regular application user with limited permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN PASSWORD 'app_passw0rd';
    END IF;
END
$$ LANGUAGE plpgsql;
