BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW lensql.v_user_info AS
SELECT
    u.username,
    u.is_admin,
    t.teacher IS NOT NULL AS is_teacher
FROM
    users u
    LEFT JOIN (
        SELECT DISTINCT
            teacher
        FROM
            teaches
    ) t ON u.username = t.teacher
WHERE
    u.can_login = TRUE;

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


COMMIT;