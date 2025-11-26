BEGIN;

SET search_path TO lensql;

-- Query stats
CREATE VIEW v_stats_queries_by_exercise AS
SELECT
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    q.query_type,
    COUNT(*) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN dataset_members dm ON dm.username = qb.username AND dm.dataset_id = e.dataset_id
WHERE
    q.query_type NOT IN ('BUILTIN', 'CHECK_SOLUTION')
GROUP BY
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    q.query_type;

-- CREATE INDEX ON v_stats_queries_by_exercise(dataset_id);
-- CREATE INDEX ON v_stats_queries_by_exercise(exercise_id);
-- CREATE INDEX ON v_stats_queries_by_exercise(username);

CREATE VIEW v_stats_queries_by_user AS
SELECT
    qb.username,
    q.query_type,
    COUNT(*) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id
WHERE
    q.query_type NOT IN ('BUILTIN', 'CHECK_SOLUTION')
GROUP BY
    qb.username,
    q.query_type;

-- CREATE INDEX ON v_stats_queries_by_user(username);

-- Message stats
CREATE VIEW v_stats_messages_by_exercise AS
SELECT
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    COUNT(m.button) AS messages,
    SUM(CASE WHEN q.query_type = 'SELECT' THEN 1 ELSE 0 END) AS messages_select,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS messages_success,
    SUM(CASE WHEN m.feedback IS NOT NULL THEN 1 ELSE 0 END) AS messages_feedback
FROM
    messages m
    JOIN queries q ON q.id = m.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN dataset_members dm ON dm.username = qb.username AND dm.dataset_id = e.dataset_id
GROUP BY
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher;

-- CREATE INDEX ON v_stats_messages_by_exercise(dataset_id);
-- CREATE INDEX ON v_stats_messages_by_exercise(exercise_id);
-- CREATE INDEX ON v_stats_messages_by_exercise(username);

CREATE VIEW v_stats_messages_by_user AS
SELECT
    qb.username,
    COUNT(m.button) AS messages,
    SUM(CASE WHEN q.query_type = 'SELECT' THEN 1 ELSE 0 END) AS messages_select,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS messages_success,
    SUM(CASE WHEN m.feedback IS NOT NULL THEN 1 ELSE 0 END) AS messages_feedback
FROM
    messages m
    JOIN queries q ON q.id = m.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
GROUP BY
    qb.username;

-- CREATE INDEX ON v_stats_messages_by_user(username);

CREATE VIEW v_stats_errors_by_exercise AS
SELECT
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    he.error_id,
    COUNT(DISTINCT q.id) AS occurrences
FROM
    has_error he
    JOIN queries q ON q.id = he.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN dataset_members dm ON dm.username = qb.username AND dm.dataset_id = e.dataset_id
GROUP BY
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    he.error_id;

CREATE VIEW v_stats_errors_by_user AS
SELECT
    qb.username,
    he.error_id,
    COUNT(DISTINCT q.id) AS occurrences
FROM
    has_error he
    JOIN queries q ON q.id = he.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
GROUP BY
    qb.username,
    he.error_id;


CREATE VIEW v_stats_error_timeline_by_exercise AS
SELECT
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    DATE(q.ts) AS day,
    he.error_id,
    COUNT(DISTINCT he.query_id) AS occurrences
FROM
    has_error he
    JOIN queries q ON q.id = he.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN dataset_members dm ON dm.username = qb.username AND dm.dataset_id = e.dataset_id
GROUP BY
    day,
    dm.dataset_id,
    qb.exercise_id,
    qb.username,
    dm.is_teacher,
    he.error_id;

CREATE VIEW v_stats_error_timeline_by_user AS
SELECT
    qb.username,
    DATE(q.ts) AS day,
    he.error_id,
    COUNT(DISTINCT he.query_id) AS occurrences
FROM
    has_error he
    JOIN queries q ON q.id = he.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
GROUP BY
    day,
    qb.username,
    he.error_id;

COMMIT;