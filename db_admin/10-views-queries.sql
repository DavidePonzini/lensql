BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW lensql.v_queries_per_user AS
SELECT
    u.username,
    COUNT(q.id) AS total_queries,
    COUNT(DISTINCT q.query) AS distinct_queries,
    COUNT(DISTINCT qb.id) AS total_query_batches
FROM
    users u
    JOIN query_batches qb ON qb.username = u.username
    JOIN queries q ON q.batch_id = qb.id
GROUP BY
    u.username;

CREATE OR REPLACE VIEW lensql.v_queries_per_user_exercise AS
SELECT
    u.username,
    qb.exercise_id,
    COUNT(q.id) AS total_queries,
    COUNT(DISTINCT q.query) AS distinct_queries,
    COUNT(DISTINCT qb.id) AS total_query_batches,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS total_successful_queries,
    SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS total_failed_queries
FROM
    users u
    JOIN query_batches qb ON qb.username = u.username
    JOIN queries q ON q.batch_id = qb.id
GROUP BY
    u.username,
    qb.exercise_id;

CREATE OR REPLACE VIEW lensql.v_queries_per_exercise AS
SELECT
    qb.exercise_id,
    COUNT(q.id) AS total_queries,
    COUNT(DISTINCT q.query) AS distinct_queries,
    COUNT(DISTINCT qb.id) AS total_query_batches,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS total_successful_queries,
    SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS total_failed_queries
FROM
    query_batches qb
    JOIN queries q  ON q.batch_id = qb.id
GROUP BY
    qb.exercise_id;

CREATE OR REPLACE VIEW lensql.v_daily_queries_per_exercise AS
SELECT
    qb.exercise_id,
    q.ts::DATE AS query_date,
    COUNT(q.id) AS total_queries,
    COUNT(DISTINCT q.query) AS distinct_queries,
    COUNT(DISTINCT qb.id) AS total_query_batches,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS total_successful_queries,
    SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS total_failed_queries
FROM
    query_batches qb
    JOIN queries q ON q.batch_id = qb.id
GROUP BY
    qb.exercise_id,
    q.ts::DATE;


COMMIT;