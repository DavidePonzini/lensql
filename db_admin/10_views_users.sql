BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW lensql.v_active_users AS
SELECT
    qb.username,
    COUNT(*) AS queries_last_30_min,
    TO_CHAR(
        NOW() - MAX(q.ts),
        'FMMI "minutes" SS "seconds ago"'
    ) AS time_since_last_query
FROM
    queries q
    JOIN query_batches qb ON q.batch_id = qb.id 
WHERE
    q.ts >= NOW() - INTERVAL '30 minutes'
GROUP BY
    qb.username
HAVING
    COUNT(*) > 0
ORDER BY
    2 DESC,
    1;

CREATE OR REPLACE VIEW lensql.v_daily_users AS
SELECT
    DATE(qb.ts) AS day,
    COUNT(DISTINCT u.username) AS users,
    COUNT(*) AS queries
FROM
    query_batches qb
    JOIN queries q ON qb.id = q.batch_id
    JOIN users u ON qb.username = u.username
WHERE
    NOT u.is_teacher
    AND NOT u.is_admin 
GROUP BY
    DATE(qb.ts)
ORDER BY
    day DESC;

COMMIT;