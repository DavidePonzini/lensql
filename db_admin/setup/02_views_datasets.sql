BEGIN;

SET search_path TO lensql;

CREATE VIEW v_dataset_list AS
SELECT
    dm.username,
    d.id,
    d.name,
    d.description,
    dm.is_owner,

    -- total number of students in the dataset
    (
        SELECT COUNT(*)
        FROM dataset_members dm2
        WHERE
            dm2.dataset_id = d.id
            AND dm2.is_owner = FALSE
            AND dm2.is_active = TRUE
    ) AS participants,

    -- total number of exercises in the dataset
    (
        SELECT COUNT(*)
        FROM exercises e2
        WHERE
            e2.dataset_id = d.id
            AND (dm.is_owner OR NOT e2.is_hidden)
    ) AS exercises,

    -- count of queries run by the user
    COUNT(q.*) FILTER (
        WHERE
            qb.username IS NOT NULL
            AND qb.username = dm.username
    ) AS queries_user,

    -- count of queries run by students (0 if the user is not a teacher)
    CASE WHEN dm.is_owner THEN
        COUNT(q.*) FILTER (
            WHERE
                qb.username IS NOT NULL
                AND qb.username IN (
                    SELECT username
                    FROM dataset_members
                    WHERE dataset_id = d.id AND is_owner = FALSE
                )
        ) ELSE 0
    END AS queries_students

FROM datasets d
JOIN dataset_members dm ON dm.dataset_id = d.id

LEFT JOIN exercises e ON e.dataset_id = d.id
LEFT JOIN query_batches qb ON qb.exercise_id = e.id
LEFT JOIN queries q ON q.batch_id = qb.id

WHERE dm.is_active = TRUE

GROUP BY dm.username, d.id, d.name, d.description, dm.is_owner, dm.joined_ts;

COMMIT;