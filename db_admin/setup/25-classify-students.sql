BEGIN;

SET search_path TO lensql;


-- Relevant errors for each query, excluding LOG errors for EXPLORATORY queries
CREATE OR REPLACE VIEW v_relevant_errors AS
SELECT
    he.query_id,
    he.error_id,
    er.category
FROM
    has_error he
    JOIN errors er
        ON er.id = he.error_id
    JOIN queries q
        ON q.id = he.query_id
WHERE
    NOT (
        er.category = '3.LOG'
        AND q.query_goal = 'EXPLORATORY'
    )
;


-- Error counts for each query with at least one relevant error
CREATE OR REPLACE VIEW v_relevant_errors_count AS
SELECT
    q.id AS query_id,
    COUNT(*) FILTER (
        WHERE category = '1.SYN'
            AND error_id <> 22
    ) AS syn,
    COUNT(*) FILTER (
        WHERE category = '2.SEM'
    ) AS sem,
    COUNT(*) FILTER (
        WHERE category = '3.LOG'
    ) AS log,
    COUNT(*) FILTER (
        WHERE category = '4.COM'
    ) AS com,
    COUNT(*) FILTER (
        WHERE error_id = 22
    ) AS missing_semicolons
FROM
    v_relevant_errors re
    JOIN queries q ON q.id = re.query_id
GROUP BY
    q.id
;    



-- ============================================================
-- ERROR RATES per USER / DATASET / QUERY GOAL
-- ============================================================

CREATE OR REPLACE VIEW v_errors AS
SELECT
    d.id AS dataset_id,
    d.name AS dataset_name,
    qb.username,
    q.query_goal,
    qb.ts BETWEEN d.activity_start_ts AND d.activity_end_ts AS is_during_lab_hours,

    COUNT(DISTINCT q.id) AS queries_total,

    -- --------------------------------------------------
    -- Queries containing at least one error of each type
    -- --------------------------------------------------

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE re.error_id IS NOT NULL
    ) AS queries_with_one_error,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE re.category = '1.SYN'
            AND re.error_id <> 22
    ) AS queries_with_one_syn,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE re.category = '2.SEM'
    ) AS queries_with_one_sem,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE re.category = '3.LOG'
            AND q.query_goal <> 'EXPLORATORY'
    ) AS queries_with_one_log,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE re.category = '4.COM'
    ) AS queries_with_one_com,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE
            re.category = '2.SEM'
            OR re.category = '3.LOG'
    ) AS queries_with_one_sem_log,

    COUNT(DISTINCT re.query_id) FILTER (
        WHERE
            re.error_id <> 22
            AND re.category IN ('1.SYN', '2.SEM', '3.LOG')
    ) AS queries_with_one_syn_sem_log,

    -- --------------------------------------------------
    -- Number of error instances
    -- --------------------------------------------------

    COUNT(*) FILTER (
        WHERE re.category = '1.SYN'
            AND re.error_id <> 22
    ) AS syn_amount,

    COUNT(*) FILTER (
        WHERE re.category = '2.SEM'
    ) AS sem_amount,

    COUNT(*) FILTER (
        WHERE re.category = '3.LOG'
            AND q.query_goal <> 'EXPLORATORY'
    ) AS log_amount,

    COUNT(*) FILTER (
        WHERE re.category = '4.COM'
    ) AS com_amount,

    COUNT(*) FILTER (
        WHERE re.error_id = 22
    ) AS missing_semicolons_amount

FROM
    queries q
    JOIN query_batches qb
        ON qb.id = q.batch_id
    JOIN exercises e
        ON e.id = qb.exercise_id
    JOIN datasets d
        ON d.id = e.dataset_id
    LEFT JOIN v_relevant_errors re
        ON re.query_id = q.id

WHERE
    q.query_type = 'SELECT'
    AND q.query_goal IN (
        'EXPLORATORY',
        'FOCUSED',
        'CHECK_SOLUTION'
    )

GROUP BY
    d.id,
    d.name,
    qb.username,
    q.query_goal,
    is_during_lab_hours
;



-- =============================================
-- Queries pre/post messages, for each exercise
-- =============================================

-- WITH
-- exercises_with_messages AS (
--     SELECT DISTINCT
--         qb.username AS username,
--         e.id AS exercise_id
--     FROM
--         exercises e
--         JOIN query_batches qb
--             ON qb.exercise_id = e.id
--         JOIN queries q
--             ON q.batch_id = qb.id
--         JOIN messages m
--             ON m.query_id = q.id
-- )

-- SELECT
--     qb.username AS username,
--     COUNT(DISTINCT e.id) AS total,
--     COUNT(DISTINCT e.id) FILTER (
--         WHERE EXISTS (
--             SELECT 1
--             FROM exercises_with_messages ewm
--             WHERE
--                 ewm.exercise_id = e.id
--                 AND ewm.username = qb.username
--         )
--     ) AS with_messages
-- FROM 
--     exercises e
--     JOIN query_batches qb
--         ON qb.exercise_id = e.id
-- WHERE
--     dataset_id IN ('CBE153UF', 'QB637QKQ', 'HVMTH9O3')
-- GROUP BY
--     username
-- ORDER BY
--     username
-- ;


CREATE OR REPLACE VIEW v_errors_after_messages AS
WITH
batches_with_errors AS (
    SELECT
        qb.id AS batch_id,
        qb.exercise_id,
        qb.username,
        COUNT(DISTINCT q.id) AS queries,
        COALESCE(SUM(syn), 0) AS syn,
        COALESCE(SUM(sem), 0) AS sem,
        COALESCE(SUM(log), 0) AS log,
        COALESCE(SUM(com), 0) AS com,
        COALESCE(SUM(missing_semicolons), 0) AS missing_semicolons
    FROM
        query_batches qb
        JOIN queries q ON q.batch_id = qb.id
        JOIN v_relevant_errors_count rec ON rec.query_id = q.id
    GROUP BY
        qb.id,
        qb.username
), batches_with_messages AS (
    SELECT DISTINCT
        e.id exercise_id,
        qb.username,
        qb.id batch_id,
        -- q.id query_id,
        m.id IS NOT NULL has_message
    FROM
        exercises e
        JOIN query_batches qb ON qb.exercise_id = e.id
        JOIN queries q ON q.batch_id = qb.id
        LEFT JOIN messages m ON m.query_id = q.id
    WHERE
        q.query_type = 'SELECT'
        AND q.query_goal IN ('FOCUSED', 'CHECK_SOLUTION')
), following_batches AS (
    SELECT DISTINCT

        bwm.exercise_id,
        bwm.username,
        bwm.batch_id,
        bwm.has_message,
        LEAD(bwm.batch_id) OVER (
            PARTITION BY bwm.exercise_id, bwm.username
            ORDER BY bwm.batch_id
        ) next_batch_id
    FROM
        batches_with_messages bwm
)
SELECT
    bwe1.exercise_id,
    bwe1.username,
    bwe1.batch_id,
    bwe1.queries queries1,
    bwe1.syn syn1,
    bwe1.sem sem1,
    bwe1.log log1,
    bwe1.com com1,
    bwe1.missing_semicolons missing_semicolons1,
    bwe2.queries queries2,
    bwe2.syn syn2,
    bwe2.sem sem2,
    bwe2.log log2,
    bwe2.com com2,
    bwe2.missing_semicolons missing_semicolons2
FROM
    batches_with_errors bwe1
    JOIN following_batches fb ON fb.batch_id = bwe1.batch_id
    JOIN batches_with_errors bwe2 ON bwe2.batch_id = fb.next_batch_id
WHERE
    fb.has_message = TRUE
;


CREATE OR REPLACE VIEW v_errors_after_messages_delta AS
SELECT
    exercise_id,
    username,
    batch_id,
    queries2 - queries1 AS queries_delta,
    syn2 - syn1 AS syn_delta,
    sem2 - sem1 AS sem_delta,
    log2 - log1 AS log_delta,
    com2 - com1 AS com_delta,
    (syn2 - syn1) + (sem2 - sem1) + (log2 - log1) + (com2 - com1) AS total_delta,
    missing_semicolons2 - missing_semicolons1 AS missing_semicolons_delta
FROM
    v_errors_after_messages
;

SELECT AVG(queries_delta) AS avg_queries_delta,
    AVG(syn_delta) AS avg_syn_delta,
    AVG(sem_delta) AS avg_sem_delta,
    AVG(log_delta) AS avg_log_delta,
    AVG(com_delta) AS avg_com_delta,
    AVG(total_delta) AS avg_total_delta,
    AVG(missing_semicolons_delta) AS avg_missing_semicolons_delta
FROM
    v_errors_after_messages_delta



COMMIT;