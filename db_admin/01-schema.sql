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
    can_use_ai BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE teaches (
    teacher VARCHAR(255) NOT NULL REFERENCES users(username),
    student VARCHAR(255) NOT NULL REFERENCES users(username),

    PRIMARY KEY (teacher, student)
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    request TEXT NOT NULL,
    dataset TEXT NOT NULL DEFAULT '',
    expected_answer TEXT NOT NULL DEFAULT '',
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE assignments (
    username VARCHAR(255) NOT NULL REFERENCES users(username),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    creation_ts TIMESTAMP NOT NULL DEFAULT NOW(),
    deadline_ts TIMESTAMP DEFAULT NULL,
    submission_ts TIMESTAMP DEFAULT NULL,

    PRIMARY KEY (username, exercise_id)
);    

CREATE TABLE query_batches (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL REFERENCES users(username),
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    exercise_id INTEGER REFERENCES exercises(id)
);

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES query_batches(id),
    query TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    result TEXT DEFAULT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id),
    answer TEXT NOT NULL,
    button VARCHAR(255) NOT NULL,
    msg_idx INTEGER NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    feedback BOOLEAN DEFAULT NULL,
    feedback_ts TIMESTAMP DEFAULT NULL
);

COMMIT;