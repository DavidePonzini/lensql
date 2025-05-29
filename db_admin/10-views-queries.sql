BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW lensql.v_queries_per_user AS
SELECT
    qb.username,
    COUNT(q.id) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    COUNT(DISTINCT qb.id) AS query_batches
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id 
GROUP BY
    qb.username;

CREATE OR REPLACE VIEW lensql.v_queries_per_user_exercise AS
SELECT
    qb.username,
    qb.exercise_id,
    COUNT(q.id) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    COUNT(DISTINCT qb.id) AS query_batches,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success,
    SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS queries_fail
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id 
GROUP BY
    qb.username,
    qb.exercise_id;

CREATE OR REPLACE VIEW lensql.v_queries_per_exercise AS
SELECT
    qb.exercise_id,
    COUNT(q.id) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    COUNT(DISTINCT qb.id) AS query_batches,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success,
    SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS queries_fail
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id 
GROUP BY
    qb.exercise_id;

-- CREATE OR REPLACE VIEW lensql.v_daily_queries_per_exercise AS
-- SELECT
--     qb.exercise_id,
--     q.ts::DATE AS query_date,
--     COUNT(q.id) AS total_queries,
--     COUNT(DISTINCT q.query) AS distinct_queries,
--     COUNT(DISTINCT qb.id) AS total_query_batches,
--     SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS total_successful_queries,
--     SUM(CASE WHEN NOT q.success THEN 1 ELSE 0 END) AS total_failed_queries
-- FROM
--     queries q
--     JOIN query_batches qb ON qb.id = q.batch_id 
-- GROUP BY
--     qb.exercise_id,
--     q.ts::DATE;

CREATE OR REPLACE VIEW lensql.v_query_types_per_user AS
SELECT
    qb.username,
    q.query_type,
    COUNT(q.id) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id
WHERE
    q.query_type <> 'BUILTIN'
GROUP BY
    qb.username,
    q.query_type
ORDER BY
    q.query_type;

CREATE OR REPLACE VIEW lensql.v_query_types_per_exercise AS
SELECT
    qb.exercise_id,
    q.query_type,
    COUNT(q.id) AS queries,
    COUNT(DISTINCT q.query) AS queries_d,
    SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
FROM
    queries q
    JOIN query_batches qb ON qb.id = q.batch_id
WHERE
    q.query_type <> 'BUILTIN'
GROUP BY
    qb.exercise_id,
    q.query_type
ORDER BY
    q.query_type;

COMMIT;