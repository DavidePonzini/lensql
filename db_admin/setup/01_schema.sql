/*
    NOTES:
    - Prevent deletion of values if they are associated with a query.
*/

BEGIN;

-- Drop existing schema if exists ------------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'lensql') THEN
        EXECUTE format('ALTER SCHEMA lensql RENAME TO lensql_bak_%s', TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS'));
    END IF;
END $$;

-- Create schema -----------------------------------------------------------------------------------------------
CREATE SCHEMA lensql;

GRANT USAGE ON SCHEMA lensql TO lensql;
ALTER DEFAULT PRIVILEGES IN SCHEMA lensql GRANT ALL ON TABLES TO lensql;
ALTER DEFAULT PRIVILEGES IN SCHEMA lensql GRANT ALL ON SEQUENCES TO lensql;

SET search_path TO lensql;

-- Function to generate random alphanumeric IDs ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION generate_alphanumeric_id(n int)
RETURNS text AS $$
DECLARE
    chars constant text := 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    result text := '';
BEGIN
    IF n <= 0 THEN
        RAISE EXCEPTION 'Length must be positive';
    END IF;

    SELECT string_agg(
        substr(chars, (random()*35)::int + 1, 1),
        ''
    )
    INTO result
    FROM generate_series(1, n);

    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Tables -------------------------------------------------------------------------------------------------------
CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    school VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,  -- allows to deactivate users without deleting them
    is_teacher BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    registration_ts TIMESTAMP NOT NULL DEFAULT NOW(),
    experience INTEGER NOT NULL DEFAULT 0,
    coins INTEGER NOT NULL DEFAULT 50
);

CREATE TABLE badges (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if badges exist
    badge VARCHAR(255) NOT NULL,        -- e.g. 'name.level' (in this way we can keep ts of each level achieved)
    ts TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (username, badge)
);

CREATE TABLE user_unique_queries (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if unique queries exist
    query_hash TEXT NOT NULL,

    PRIMARY KEY (username, query_hash)
);

CREATE TABLE datasets (
    id TEXT PRIMARY KEY DEFAULT generate_alphanumeric_id(8),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    dataset TEXT DEFAULT NULL
);

CREATE TABLE dataset_members (
    username VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,
    dataset_id TEXT NOT NULL REFERENCES datasets(id) ON UPDATE CASCADE ON DELETE RESTRICT,  -- dataset can only be deleted if no members are present
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_owner BOOLEAN NOT NULL DEFAULT FALSE,
    joined_ts TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (username, dataset_id)
);


CREATE TABLE errors (
    id INTEGER PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    subcategory VARCHAR(255) NOT NULL,
    error VARCHAR(255) NOT NULL
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES datasets(id) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of dataset if exercises are assigned
    is_hidden BOOLEAN NOT NULL DEFAULT TRUE,
    title VARCHAR(255) NOT NULL,
    request TEXT NOT NULL,
    solutions TEXT NOT NULL DEFAULT '[]',  -- JSON array of solution strings
    search_path TEXT NOT NULL DEFAULT 'public',
    created_by VARCHAR(255) NOT NULL REFERENCES users(username) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of user if exercises are assigned
    created_ts TIMESTAMP NOT NULL DEFAULT NOW(),
    generation_difficulty INTEGER DEFAULT NULL,
    generation_error INTEGER DEFAULT NULL REFERENCES errors(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE learning_objectives (
    id VARCHAR(255) NOT NULL PRIMARY KEY
);

CREATE TABLE has_learning_objective (
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    objective_id VARCHAR(255) NOT NULL REFERENCES learning_objectives(id) ON UPDATE CASCADE ON DELETE RESTRICT,  -- prevent deletion of objective if it is associated with an exercise

    PRIMARY KEY (exercise_id, objective_id)
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


CREATE TABLE has_error(
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    error_id INTEGER NOT NULL REFERENCES errors(id) ON DELETE CASCADE ON UPDATE CASCADE,
    details TEXT[] DEFAULT NULL
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