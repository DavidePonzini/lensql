BEGIN;

SET search_path TO lensql;

CREATE VIEW v_dataset_list AS
SELECT
    dm.username,
    d.id,
    d.name,
    d.description,
    d.search_path,
    dm.is_owner,
    dm.joined_ts,

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

CREATE VIEW v_generated_exercises AS
SELECT
    e.dataset_id,
    e.generation_error,
    ARRAY_AGG(e.generation_difficulty ORDER BY e.generation_difficulty) AS generation_difficulties
FROM exercises e
WHERE
    e.generation_error IS NOT NULL
    AND e.generation_difficulty IS NOT NULL
GROUP BY e.dataset_id, e.generation_error
ORDER BY e.dataset_id, e.generation_error;

CREATE VIEW v_dataset_completion AS
WITH solved_exercises AS (
    SELECT
        qb.username,
        e.id AS exercise_id
    FROM exercises e
    JOIN query_batches qb ON qb.exercise_id = e.id
    JOIN queries q ON q.batch_id = qb.id
    JOIN exercise_solutions es ON es.id = q.id
    WHERE es.is_correct = TRUE
    GROUP BY e.id, qb.username
), dataset_progress AS (
    SELECT
        dm.username,
        d.id AS dataset_id,
        COUNT(DISTINCT e.id) AS total_exercises,
        COUNT(DISTINCT se.exercise_id) AS solved_exercises
    FROM datasets d
    JOIN dataset_members dm ON dm.dataset_id = d.id
    JOIN exercises e ON e.dataset_id = d.id AND e.is_hidden = FALSE
    LEFT JOIN solved_exercises se ON se.exercise_id = e.id AND se.username = dm.username
    WHERE
        dm.is_active = TRUE
        AND NOT dm.is_owner
    GROUP BY dm.username, d.id
)

SELECT
    username,
    dataset_id,
    solved_exercises AS solved,
    total_exercises - solved_exercises AS remaining,
    ((solved_exercises::DECIMAL / total_exercises) * 100)::DECIMAL(5,2) AS completion
FROM dataset_progress
WHERE
    total_exercises > 0
    AND solved_exercises > 0
ORDER BY
    completion DESC,
    dataset_id,
    username;



COMMIT;