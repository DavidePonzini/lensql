CREATE OR REPLACE FUNCTION setup_db_user(username TEXT, user_password TEXT DEFAULT 'bd2025')
RETURNS void AS $$
DECLARE
BEGIN
    -- Create user if not exists
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = username) THEN
        EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L;', username, user_password);
    END IF;

    -- Grant all privileges on the database (assumes DB name = username)
    EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I;', username, username);

    -- Restrict access to common system databases
    EXECUTE format('REVOKE CONNECT ON DATABASE postgres FROM %I;', username);
    EXECUTE format('REVOKE CONNECT ON DATABASE template1 FROM %I;', username);
    EXECUTE format('REVOKE CONNECT ON DATABASE template0 FROM %I;', username);
END;
$$ LANGUAGE plpgsql;
