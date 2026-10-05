BEGIN;

SET search_path TO lensql;

-- ============================================================
-- ERROR RATES per USER / DATASET / QUERY GOAL
-- ============================================================

CREATE OR REPLACE VIEW v_errors AS
-- valid_errors CTE: exclude LOG errors for EXPLORATORY queries, since they are not considered errors in that context.
WITH valid_errors AS (
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
)

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

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE ve.error_id IS NOT NULL
    ) AS queries_with_one_error,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE ve.category = '1.SYN'
            AND ve.error_id <> 22
    ) AS queries_with_one_syn,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE ve.category = '2.SEM'
    ) AS queries_with_one_sem,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE ve.category = '3.LOG'
            AND q.query_goal <> 'EXPLORATORY'
    ) AS queries_with_one_log,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE ve.category = '4.COM'
    ) AS queries_with_one_com,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE
            ve.category = '2.SEM'
            OR ve.category = '3.LOG'
    ) AS queries_with_one_sem_log,

    COUNT(DISTINCT ve.query_id) FILTER (
        WHERE
            ve.error_id <> 22
            AND ve.category IN ('1.SYN', '2.SEM', '3.LOG')
    ) AS queries_with_one_syn_sem_log,

    -- --------------------------------------------------
    -- Number of error instances
    -- --------------------------------------------------

    COUNT(*) FILTER (
        WHERE ve.category = '1.SYN'
            AND ve.error_id <> 22
    ) AS syn_amount,

    COUNT(*) FILTER (
        WHERE ve.category = '2.SEM'
    ) AS sem_amount,

    COUNT(*) FILTER (
        WHERE ve.category = '3.LOG'
            AND q.query_goal <> 'EXPLORATORY'
    ) AS log_amount,

    COUNT(*) FILTER (
        WHERE ve.category = '4.COM'
    ) AS com_amount,

    COUNT(*) FILTER (
        WHERE ve.error_id = 22
    ) AS missing_semicolons_amount

FROM
    queries q
    JOIN query_batches qb
        ON qb.id = q.batch_id
    JOIN exercises e
        ON e.id = qb.exercise_id
    JOIN datasets d
        ON d.id = e.dataset_id
    LEFT JOIN valid_errors ve
        ON ve.query_id = q.id

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

COMMIT;