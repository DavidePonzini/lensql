BEGIN;

SET search_path TO lensql;


-- Query stats
CREATE MATERIALIZED VIEW v_stats_queries_by_exercise AS
SELECT
    cm.class_id,
    qb.exercise_id,
    qb.username,
    q.query_type,
    COUNT(*) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    lensql.queries q
    JOIN lensql.query_batches qb ON qb.id = q.batch_id
    JOIN lensql.exercises e ON qb.exercise_id = e.id
    JOIN lensql.class_members cm ON cm.username = qb.username AND cm.class_id = e.class_id
WHERE
    q.query_type <> 'BUILTIN'
    AND cm.is_teacher = FALSE
GROUP BY
    cm.class_id,
    qb.exercise_id,
    qb.username,
    q.query_type;

CREATE INDEX ON v_stats_queries_by_exercise(class_id);
CREATE INDEX ON v_stats_queries_by_exercise(exercise_id);
CREATE INDEX ON v_stats_queries_by_exercise(username);

CREATE MATERIALIZED VIEW v_stats_queries_by_user AS
SELECT
    qb.username,
    q.query_type,
    COUNT(*) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    lensql.queries q
    JOIN lensql.query_batches qb ON qb.id = q.batch_id
WHERE
    q.query_type <> 'BUILTIN'
GROUP BY
    qb.username,
    q.query_type;

CREATE INDEX ON v_stats_queries_by_user(username);

-- Message stats
CREATE MATERIALIZED VIEW v_stats_messages_by_exercise AS
SELECT
    cm.class_id,
    qb.exercise_id,
    qb.username,
    COUNT(m.button) AS messages,
    SUM(CASE WHEN q.query_type = 'SELECT' THEN 1 ELSE 0 END) AS messages_select,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS messages_success,
    SUM(CASE WHEN m.feedback IS NOT NULL THEN 1 ELSE 0 END) AS messages_feedback
FROM
    lensql.messages m
    JOIN lensql.queries q ON q.id = m.query_id
    JOIN lensql.query_batches qb ON qb.id = q.batch_id
    JOIN lensql.exercises e ON qb.exercise_id = e.id
    JOIN lensql.class_members cm ON cm.username = qb.username AND cm.class_id = e.class_id
WHERE
    cm.is_teacher = FALSE
GROUP BY
    cm.class_id,
    qb.exercise_id,
    qb.username;

CREATE INDEX ON v_stats_messages_by_exercise(class_id);
CREATE INDEX ON v_stats_messages_by_exercise(exercise_id);
CREATE INDEX ON v_stats_messages_by_exercise(username);

CREATE MATERIALIZED VIEW v_stats_messages_by_user AS
SELECT
    qb.username,
    COUNT(m.button) AS messages,
    SUM(CASE WHEN q.query_type = 'SELECT' THEN 1 ELSE 0 END) AS messages_select,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS messages_success,
    SUM(CASE WHEN m.feedback IS NOT NULL THEN 1 ELSE 0 END) AS messages_feedback
FROM
    lensql.messages m
    JOIN lensql.queries q ON q.id = m.query_id
    JOIN lensql.query_batches qb ON qb.id = q.batch_id
GROUP BY
    qb.username;

CREATE INDEX ON v_stats_messages_by_user(username);


COMMIT;