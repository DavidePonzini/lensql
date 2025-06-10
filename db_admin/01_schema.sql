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
    is_disabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_teacher BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    experience INTEGER NOT NULL DEFAULT 0,
    coins INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE teaches (
    teacher VARCHAR(255) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    student VARCHAR(255) NOT NULL REFERENCES users(username) ON DELETE CASCADE,

    PRIMARY KEY (teacher, student)
);

CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dataset TEXT NOT NULL DEFAULT '-- No dataset provided',
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE has_dataset (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,

    PRIMARY KEY (username, dataset_id)
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    request TEXT NOT NULL,
    dataset_id INTEGER REFERENCES datasets(id) DEFAULT NULL,
    expected_answer TEXT NOT NULL DEFAULT '',
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE assigned_to (
    username VARCHAR(255) NOT NULL REFERENCES users(username),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    submission_ts TIMESTAMP DEFAULT NULL,

    PRIMARY KEY (username, exercise_id)
);

CREATE TABLE learning_objectives (
    objective VARCHAR(255) NOT NULL PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE has_learning_objective (
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    objective VARCHAR(255) NOT NULL REFERENCES learning_objectives(objective),

    PRIMARY KEY (exercise_id, objective)
);

CREATE TABLE query_batches (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL REFERENCES users(username),
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id)
);

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES query_batches(id),
    query TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    result TEXT DEFAULT NULL,
    query_type VARCHAR(50) NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE errors (
    id INTEGER PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    subcategory VARCHAR(255) NOT NULL,
    error VARCHAR(255) NOT NULL
);

CREATE TABLE has_error(
    query_id INTEGER NOT NULL REFERENCES queries(id),
    error_id INTEGER NOT NULL REFERENCES errors(id),

    PRIMARY KEY (query_id, error_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id),
    answer TEXT NOT NULL,
    button VARCHAR(255) NOT NULL,
    msg_idx INTEGER NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    feedback BOOLEAN DEFAULT NULL,
    feedback_ts TIMESTAMP DEFAULT NULL
);

COMMIT;