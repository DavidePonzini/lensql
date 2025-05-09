BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'lensql') THEN
        EXECUTE format('ALTER SCHEMA lensql RENAME TO lensql_bak_%s', TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS'));
    END IF;
END $$;
CREATE SCHEMA lensql;

GRANT USAGE ON SCHEMA lensql TO lensql;
ALTER DEFAULT PRIVILEGES IN SCHEMA lensql GRANT ALL ON TABLES TO lensql;
ALTER DEFAULT PRIVILEGES IN SCHEMA lensql GRANT ALL ON SEQUENCES TO lensql;

SET search_path TO lensql;

CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    can_login BOOLEAN NOT NULL DEFAULT TRUE,
    can_use_ai BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL REFERENCES users(username),
    query TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    exercise_id INTEGER DEFAULT NULL
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id),
    content TEXT NOT NULL,
    button VARCHAR(255) NOT NULL,
    data TEXT DEFAULT NULL,
    chat_id INTEGER NOT NULL,
    msg_id INTEGER NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    feedback BOOLEAN DEFAULT NULL,
    feedback_ts TIMESTAMP DEFAULT NULL
);

COMMIT;