BEGIN;

SET search_path to lensql;

CREATE OR REPLACE VIEW v_button_presses_per_user AS
SELECT
    m.button,
    COUNT(*)::float / (
        -- Count the number of unique users who have pressed any button
        SELECT COUNT(DISTINCT qb.username)
        FROM
            query_batches qb
            JOIN queries q ON qb.id = q.batch_id
            JOIN messages m2 ON q.id = m2.query_id
    ) AS presses_per_user,
    -- percentage of total button presses for this button
    (COUNT(*)::float / (
        SELECT COUNT(*)
        FROM messages
    )) * 100 AS percentage_of_total_presses
FROM
    messages m
GROUP BY
    m.button
ORDER BY
    presses_per_user DESC;

CREATE OR REPLACE VIEW v_success_rate_by_type AS
SELECT
    query_type,
    COUNT(*) FILTER (WHERE success is true) AS successes,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE success is true)::float / COUNT(*) AS success_rate
FROM
    queries 
GROUP BY
    query_type
ORDER BY
    query_type;

CREATE OR REPLACE VIEW v_success_rate_by_goal AS
SELECT
    query_goal,
    COUNT(*) FILTER (WHERE success is true) AS successes,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE success is true)::float / COUNT(*) AS success_rate
FROM
    queries 
GROUP BY
    query_goal
ORDER BY
    query_goal;

CREATE OR REPLACE VIEW v_query_batches_during_lab_hours AS
SELECT
    qb.id AS batch_id,
    lh.lab_name
FROM
    query_batches qb
    JOIN lab_hours lh ON qb.ts >= lh.start_ts AND qb.ts <= lh.end_ts;

CREATE OR REPLACE VIEW v_messages_per_dataset AS
SELECT
    d.name,
    q.query_goal,
    q.query_type,
    count(m.id) messages,
    count(DISTINCT q.id) AS queries,
    count(m.id)::float / count(DISTINCT q.id) AS messages_per_query
FROM
    messages m
    RIGHT JOIN queries q ON q.id = m.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON e.id = qb.exercise_id
    JOIN datasets d ON d.id = e.dataset_id
GROUP BY d.name, q.query_goal, q.query_type
HAVING count(m.id) > 0
ORDER BY name, query_goal, query_type;

CREATE OR REPLACE VIEW v_messages_per_dataset_during_lab_hours AS
SELECT
    d.name,
    q.query_goal,
    q.query_type,
    count(m.id) messages,
    count(DISTINCT q.id) AS queries,
    count(m.id)::float / count(DISTINCT q.id) AS messages_per_query
FROM
    messages m
    RIGHT JOIN queries q ON q.id = m.query_id
    JOIN query_batches qb ON qb.id = q.batch_id
    JOIN exercises e ON e.id = qb.exercise_id
    JOIN datasets d ON d.id = e.dataset_id
    JOIN v_query_batches_during_lab_hours lq ON lq.batch_id = qb.id
GROUP BY d.name, q.query_goal, q.query_type
HAVING count(m.id) > 0
ORDER BY name, query_goal, query_type;

CREATE OR REPLACE VIEW v_generated_exercises_errors AS
SELECT d.name AS dataset_name,
    e.dataset_id,
    e.id AS exercise_id,
    e.title,
    e.generation_error,
    e.generation_difficulty,
    he.error_id,
    count(he.error_id) AS error_count,
        CASE
            WHEN count(he.error_id) = 0 THEN NULL::double precision
            ELSE count(he.error_id) FILTER (WHERE he.error_id = e.generation_error) OVER (PARTITION BY d.name, e.id)::double precision / count(he.error_id)::double precision
        END AS expected_error_rate
FROM exercises e
    JOIN datasets d ON d.id = e.dataset_id
    JOIN query_batches qb ON qb.exercise_id = e.id
    JOIN queries q ON q.batch_id = qb.id
    LEFT JOIN has_error he ON q.id = he.query_id
WHERE
    e.generation_error IS NOT NULL
    AND e.generation_difficulty IS NOT NULL
GROUP BY
    d.name,
    e.dataset_id,
    e.id,
    e.title,
    e.generation_error,
    e.generation_difficulty,
    he.error_id
ORDER BY
d.name,
("substring"(e.title::text, '\d+'::text)::integer);

CREATE OR REPLACE VIEW v_generated_exercises_expected_errors AS
SELECT
    d.name AS dataset_name,
    e.dataset_id,
    e.id AS exercise_id,
    e.title,
    e.generation_error,
    e.generation_difficulty,
    CASE WHEN COUNT(he.error_id) = 0
        THEN NULL
        ELSE (COUNT(he.error_id) FILTER (WHERE he.error_id = e.generation_error))::float / COUNT(he.error_id)
    END AS expected_error_rate
FROM
    exercises e
    JOIN datasets d ON d.id = e.dataset_id
    JOIN query_batches qb ON qb.exercise_id = e.id
    JOIN queries q ON q.batch_id = qb.id
    LEFT JOIN has_error he ON q.id = he.query_id
WHERE
    e.generation_error IS NOT NULL
    AND e.generation_difficulty IS NOT NULL
GROUP BY
    d.name,
    e.dataset_id,
    e.id,
    e.title,
    e.generation_error,
    e.generation_difficulty;

CREATE OR REPLACE VIEW v_exercise_solution_attempts AS
WITH first_solution_ts AS (     -- users who solved the exercise and when they solved it for the first time
    SELECT
        qb.exercise_id,
        qb.username,
        MIN(q.ts) AS solution_ts
    FROM
        exercise_solutions es
        JOIN queries q ON es.id = q.id
        JOIN query_batches qb ON q.batch_id = qb.id
    WHERE
        es.is_correct = TRUE
    GROUP BY
        qb.exercise_id,
        qb.username
),
queries_before_solution AS (    -- number of queries before the first correct solution, for users who solved the exercise
    SELECT
        qb.exercise_id,
        qb.username,
        COUNT(*) AS total_queries
    FROM
        queries q
        JOIN query_batches qb ON q.batch_id = qb.id
        JOIN first_solution_ts fs ON fs.exercise_id = qb.exercise_id AND fs.username = qb.username AND q.ts < fs.solution_ts
    WHERE
        q.query_type = 'SELECT'
        AND q.query_goal NOT IN ('CHECK_SOLUTION', 'BUILTIN', 'EXPLORATORY')
    GROUP BY
        qb.exercise_id,
        qb.username
),
attempts_before_solution AS (   -- number of check solutions before the first correct solution, for users who solved the exercise
    SELECT
        fs.exercise_id,
        fs.username,
        COUNT(*) AS attempts
    FROM
        queries q
        JOIN query_batches qb ON q.batch_id = qb.id
        JOIN first_solution_ts fs ON qb.exercise_id = fs.exercise_id AND qb.username = fs.username AND q.ts < fs.solution_ts
    WHERE
        q.query_goal = 'CHECK_SOLUTION'
    GROUP BY
        fs.exercise_id,
        fs.username
)
SELECT
    fs.exercise_id,
    fs.username,
    COALESCE(a.attempts, 0) AS attempts_before_solution,
    COALESCE(q.total_queries, 0) AS queries_before_solution
FROM
    first_solution_ts fs
    LEFT JOIN attempts_before_solution a ON fs.exercise_id = a.exercise_id AND fs.username = a.username
    LEFT JOIN queries_before_solution q ON fs.exercise_id = q.exercise_id AND fs.username = q.username;

CREATE OR REPLACE VIEW v_exercise_solution_time AS
WITH first_visit AS (
    SELECT
        e.id AS exercise_id,
        qb.username,
        MIN(nl.ts) as ts
    FROM
        exercises e
        JOIN query_batches qb ON qb.exercise_id = e.id
        JOIN navigation_logs nl ON nl.username = qb.username AND nl.url = CONCAT('/exercises/', e.id)
    WHERE
        nl.event = 'VISIT'
    GROUP BY
        e.id,
        qb.username
),
first_query AS (            -- use as fallback if we somehow missed the visit event
    SELECT
        e.id AS exercise_id,
        qb.username,
        MIN(q.ts) as ts
    FROM
        exercises e
        JOIN query_batches qb ON qb.exercise_id = e.id
        JOIN queries q ON qb.id = q.batch_id
    GROUP BY
        e.id,
        qb.username
),
first_success AS (
    SELECT
        e.id AS exercise_id,
        qb.username,
        MIN(es.solution_ts) as ts
    FROM
        exercises e
        JOIN query_batches qb ON qb.exercise_id = e.id
        JOIN queries q ON qb.id = q.batch_id
        JOIN exercise_solutions es ON es.id = q.id
    WHERE
        es.is_correct = TRUE
    GROUP BY
        e.id,
        qb.username
)
SELECT
    first_visit.exercise_id,
    first_visit.username,
    AVG(EXTRACT(EPOCH FROM (first_success.ts - LEAST(first_visit.ts, first_query.ts))) / 60) AS avg_time_to_solution_minutes
FROM
    first_visit
    JOIN first_query ON first_visit.exercise_id = first_query.exercise_id AND first_visit.username = first_query.username
    JOIN first_success ON first_visit.exercise_id = first_success.exercise_id AND first_visit.username = first_success.username
WHERE
    first_success.ts - LEAST(first_visit.ts, first_query.ts) < INTERVAL '2 hours'
GROUP BY
    first_visit.exercise_id, first_visit.username;


CREATE OR REPLACE VIEW v_solution_errors AS
SELECT
    q.id AS query_id,
    qb.exercise_id,
    qb.username,
    he.error_id,
    e.category,
    e.name
FROM
    exercise_solutions es
    JOIN queries q ON es.id = q.id
    JOIN query_batches qb ON q.batch_id = qb.id
    LEFT JOIN has_error he ON q.id = he.query_id
    LEFT JOIN errors e ON he.error_id = e.id
WHERE
    es.is_correct = TRUE;

COMMIT;