BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW v_queries_during_lab_hours AS
SELECT
    d.id AS activity_id,
    d.name AS activity_name,
    q.id,
    CASE WHEN d.activity_start_ts IS NULL OR d.activity_end_ts IS NULL THEN NULL
         ELSE q.ts BETWEEN d.activity_start_ts AND d.activity_end_ts
    END AS is_during_lab_hours
FROM queries q
JOIN query_batches qb ON qb.id = q.batch_id
JOIN exercises e ON qb.exercise_id = e.id
JOIN activities d ON d.id = e.activity_id
;

CREATE OR REPLACE VIEW v_queries_during_lab_hours_by_activity AS
SELECT
    activity_id,
    activity_name,
    COUNT(*) FILTER (WHERE is_during_lab_hours) AS queries_during_lab_hours,
    COUNT(*) AS queries_total
FROM v_queries_during_lab_hours
WHERE is_during_lab_hours IS NOT NULL
GROUP BY
    GROUPING SETS (
        (activity_id, activity_name),
        ()
    )
ORDER BY activity_name
;


COMMIT;