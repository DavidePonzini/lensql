BEGIN;

SET search_path TO lensql;


-- Query stats
CREATE VIEW v_stats_queries_by_exercise AS
SELECT
    cm.class_id,
    qb.exercise_id,
    qb.username,
    q.query_type,
    COUNT(*) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN class_members cm ON cm.username = qb.username AND cm.class_id = e.class_id
WHERE
    q.query_type NOT IN ('BUILTIN', 'CHECK_SOLUTION')
    AND cm.is_teacher = FALSE
GROUP BY
    cm.class_id,
    qb.exercise_id,
    qb.username,
    q.query_type;

-- CREATE INDEX ON v_stats_queries_by_exercise(class_id);
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
    cm.class_id,
    qb.exercise_id,
    qb.username,
    COUNT(m.button) AS messages,
    SUM(CASE WHEN q.query_type = 'SELECT' THEN 1 ELSE 0 END) AS messages_select,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS messages_success,
    SUM(CASE WHEN m.feedback IS NOT NULL THEN 1 ELSE 0 END) AS messages_feedback
FROM
    messages m
    JOIN queries q ON q.id = m.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON qb.exercise_id = e.id
    JOIN class_members cm ON cm.username = qb.username AND cm.class_id = e.class_id
WHERE
    cm.is_teacher = FALSE
GROUP BY
    cm.class_id,
    qb.exercise_id,
    qb.username;

-- CREATE INDEX ON v_stats_messages_by_exercise(class_id);
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

CREATE VIEW v_errors_by_user AS
SELECT
    qb.username,
    q.id AS query_id,
    e.*,
    he.details
FROM
    query_batches qb
    JOIN queries q ON q.batch_id = qb.id
    JOIN has_error he ON he.query_id = q.id
    JOIN errors e ON e.id = he.error_id
ORDER BY
    q.id DESC,
    e.id;


COMMIT;