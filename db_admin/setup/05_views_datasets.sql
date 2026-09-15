BEGIN;

SET search_path TO lensql;

CREATE OR REPLACE VIEW v_dataset_list AS
WITH participant_counts AS (
    SELECT
        dataset_id,
        COUNT(*) AS participants
    FROM dataset_members
    WHERE
        is_owner = FALSE
        AND is_active = TRUE
    GROUP BY dataset_id
),

exercise_counts AS (
    SELECT
        dataset_id,
        COUNT(*) AS exercises_all,
        COUNT(*) FILTER (WHERE is_hidden = FALSE) AS exercises_visible
    FROM exercises
    GROUP BY dataset_id
),

query_counts AS (
    SELECT
        e.dataset_id,
        qb.username,
        COUNT(*) AS queries
    FROM exercises e
    JOIN query_batches qb
        ON qb.exercise_id = e.id
    JOIN queries q
        ON q.batch_id = qb.id
    WHERE qb.username IS NOT NULL
    GROUP BY
        e.dataset_id,
        qb.username
),

student_query_counts AS (
    SELECT
        qc.dataset_id,
        SUM(qc.queries)::BIGINT AS queries
    FROM query_counts qc
    JOIN dataset_members dm
        ON dm.dataset_id = qc.dataset_id
        AND dm.username = qc.username
    WHERE dm.is_owner = FALSE
    GROUP BY qc.dataset_id
)

SELECT
    dm.username,
    d.id,
    d.name,
    d.description,
    d.search_path,
    d.dbms,
    dm.is_owner,
    dm.joined_ts,

    -- total number of active students in the dataset
    COALESCE(pc.participants, 0) AS participants,

    -- owners see all exercises; students only see non-hidden ones
    CASE
        WHEN dm.is_owner
            THEN COALESCE(ec.exercises_all, 0)
        ELSE
            COALESCE(ec.exercises_visible, 0)
    END AS exercises,

    -- number of queries run by this user in this dataset
    COALESCE(qc.queries, 0) AS queries_user,

    -- number of queries run by students, only exposed to owners
    CASE
        WHEN dm.is_owner
            THEN COALESCE(sqc.queries, 0)
        ELSE 0
    END AS queries_students

FROM dataset_members dm
JOIN datasets d
    ON d.id = dm.dataset_id

LEFT JOIN participant_counts pc
    ON pc.dataset_id = d.id

LEFT JOIN exercise_counts ec
    ON ec.dataset_id = d.id

LEFT JOIN query_counts qc
    ON qc.dataset_id = d.id
    AND qc.username = dm.username

LEFT JOIN student_query_counts sqc
    ON sqc.dataset_id = d.id

WHERE dm.is_active = TRUE;

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