BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW v_queries_during_lab_hours AS
SELECT
    d.id AS dataset_id,
    d.name AS dataset_name,
    q.id,
    CASE WHEN d.activity_start_ts IS NULL OR d.activity_end_ts IS NULL THEN NULL
         ELSE q.ts BETWEEN d.activity_start_ts AND d.activity_end_ts
    END AS is_during_lab_hours
FROM queries q
JOIN query_batches qb ON qb.id = q.batch_id
JOIN exercises e ON qb.exercise_id = e.id
JOIN datasets d ON d.id = e.dataset_id
;

CREATE OR REPLACE VIEW v_queries_during_lab_hours_by_dataset AS
SELECT
    dataset_id,
    dataset_name,
    COUNT(*) FILTER (WHERE is_during_lab_hours) AS queries_during_lab_hours,
    COUNT(*) AS queries_total
FROM v_queries_during_lab_hours
WHERE is_during_lab_hours IS NOT NULL
GROUP BY
    GROUPING SETS (
        (dataset_id, dataset_name),
        ()
    )
ORDER BY dataset_name
;


COMMIT;