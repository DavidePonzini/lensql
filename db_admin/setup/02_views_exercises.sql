BEGIN;

SET search_path TO lensql;

CREATE VIEW v_exercise_solution_ts AS
WITH exercise_queries AS (
    SELECT
        qb.exercise_id,
        qb.username,
        q.id AS query_id,
        q.query_type,
        qb.ts AS ts,
        is_correct
    FROM queries q
    JOIN query_batches qb ON q.batch_id = qb.id
    LEFT JOIN exercise_solutions es ON es.id = q.id
), first_opened AS (
    SELECT
        exercise_id,
        username,
        MIN(ts) AS opened_ts
    FROM opened_exercises
    GROUP BY exercise_id, username
), first_queries_ts AS (
    SELECT
        exercise_id,
        username,
        MIN(ts) AS first_query_ts,
        MIN(ts) FILTER (WHERE query_type = 'SELECT') AS first_select_ts,
        MIN(ts) FILTER (WHERE query_type = 'CHECK_SOLUTION') AS first_attempt_ts,
        MIN(ts) FILTER (WHERE query_type = 'CHECK_SOLUTION' AND is_correct = TRUE) AS solution_ts
    FROM exercise_queries
    GROUP BY exercise_id, username
), query_counts AS (
    SELECT
        exercise_id,
        username,
        COUNT(*) FILTER (WHERE query_type != 'CHECK_SOLUTION' AND ts < first_attempt_ts) AS queries_before_first_attempt,
        COUNT(*) FILTER (WHERE query_type != 'CHECK_SOLUTION' AND ts < solution_ts) AS queries_before_solution,
        COUNT(*) FILTER (WHERE query_type = 'CHECK_SOLUTION' AND ts < solution_ts) AS attempts_before_solution,
        COUNT(*) FILTER (WHERE query_type != 'CHECK_SOLUTION' AND ts > solution_ts) AS queries_after_solution,
        COUNT(*) FILTER (WHERE query_type = 'CHECK_SOLUTION' AND ts > solution_ts) AS attempts_after_solution
    FROM exercise_queries
    JOIN first_queries_ts USING (exercise_id, username)
    GROUP BY exercise_id, username
)
SELECT
    exercise_id,
    username,
    opened_ts,
    first_query_ts,
    first_select_ts,
    first_attempt_ts,
    queries_before_first_attempt,
    queries_before_solution,
    attempts_before_solution,
    solution_ts,
    queries_after_solution,
    attempts_after_solution
FROM
    first_opened
    JOIN first_queries_ts USING (exercise_id, username)
    JOIN query_counts USING (exercise_id, username)
ORDER BY exercise_id, username;


COMMIT;