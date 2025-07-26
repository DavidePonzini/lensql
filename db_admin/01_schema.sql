/*
    NOTES:
    - Prevent deletion of values if they are associated with a query.
*/

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
    email VARCHAR(255) DEFAULT NULL,
    school VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    registration_ts TIMESTAMP NOT NULL DEFAULT NOW(),
    experience INTEGER NOT NULL DEFAULT 0,
    coins INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE badges (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if badges exist
    badge VARCHAR(255) NOT NULL,
    rank INTEGER NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (username, badge, rank)
);

CREATE TABLE user_unique_queries (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if unique queries exist
    query_hash TEXT NOT NULL,

    PRIMARY KEY (username, query_hash)
);

CREATE TABLE classes (
    id CHAR(8) PRIMARY KEY DEFAULT UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 8)),
    name VARCHAR(255) NOT NULL,
    dataset TEXT DEFAULT NULL
);

CREATE TABLE class_members (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,
    class_id CHAR(8) NOT NULL REFERENCES classes(id) ON UPDATE CASCADE ON DELETE RESTRICT,  -- class can only be deleted if no members are present
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_teacher BOOLEAN NOT NULL DEFAULT FALSE,
    joined_ts TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (username, class_id)
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    class_id CHAR(8) NOT NULL REFERENCES classes(id) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of class if exercises are assigned
    is_hidden BOOLEAN NOT NULL DEFAULT TRUE,
    title VARCHAR(255) NOT NULL,
    request TEXT NOT NULL,
    solution TEXT DEFAULT NULL,
    created_by VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if exercises are assigned
    created_ts TIMESTAMP NOT NULL DEFAULT NOW(),
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE exercise_submissions (
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE RESTRICT,  -- prevent deletion of exercise if submissions exist
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if submissions exist
    submission_ts TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (exercise_id, username)
);

CREATE TABLE learning_objectives (
    objective VARCHAR(255) NOT NULL PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE has_learning_objective (
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    objective VARCHAR(255) NOT NULL REFERENCES learning_objectives(objective) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of objective if it is associated with an exercise

    PRIMARY KEY (exercise_id, objective)
);

CREATE TABLE query_batches (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if queries exist
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE RESTRICT   -- prevent deletion of exercise if queries exist
);

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES query_batches(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    search_path TEXT DEFAULT NULL,
    success BOOLEAN,        -- supports NULL for queries that are not executed (e.g. when checking solutions in particular cases)
    result TEXT DEFAULT NULL,
    query_type VARCHAR(50) NOT NULL,
    query_goal VARCHAR(255) DEFAULT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW()
);

-- solutions attempted by students
CREATE TABLE exercise_solutions (
    id INTEGER NOT NULL REFERENCES queries(id) PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE RESTRICT,  -- prevent deletion of exercise if solutions exist
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if solutions exist
    is_correct BOOLEAN,
    solution_ts TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE query_context_columns (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    column_type TEXT NOT NULL,
    numeric_precision INTEGER,
    numeric_scale INTEGER,
    foreign_key_schema TEXT DEFAULT NULL,
    foreign_key_table TEXT DEFAULT NULL,
    foreign_key_column TEXT DEFAULT NULL,
    is_nullable BOOLEAN NOT NULL
);

CREATE TABLE query_context_columns_unique (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    constraint_type VARCHAR(32) NOT NULL,
    columns TEXT[] NOT NULL
);
    

CREATE TABLE errors (
    id INTEGER PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    subcategory VARCHAR(255) NOT NULL,
    error VARCHAR(255) NOT NULL
);

CREATE TABLE has_error(
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    error_id INTEGER NOT NULL REFERENCES errors(id) ON DELETE RESTRICT,  -- prevent deletion of error if it is associated with a query

    PRIMARY KEY (query_id, error_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    button VARCHAR(255) NOT NULL,
    msg_idx INTEGER NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    feedback BOOLEAN DEFAULT NULL,
    feedback_ts TIMESTAMP DEFAULT NULL
);

COMMIT;