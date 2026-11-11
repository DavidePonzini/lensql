BEGIN;

SET search_path TO lensql;

CREATE INDEX ON activity_members (activity_id, is_owner, is_active);
CREATE INDEX ON exercises (activity_id);
CREATE INDEX ON query_batches (username);
CREATE INDEX ON query_batches (exercise_id);
CREATE INDEX ON queries (batch_id);
CREATE INDEX ON query_context_columns (query_id);
CREATE INDEX ON query_context_columns_unique (query_id);
CREATE INDEX ON query_context_functions (query_id);
CREATE INDEX ON has_error (query_id);
CREATE INDEX ON messages (query_id);

COMMIT;