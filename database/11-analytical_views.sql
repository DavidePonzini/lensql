BEGIN;

SET search_path to lensql;

CREATE OR REPLACE VIEW v_queries AS
SELECT 
    count(*) AS total_queries,
    count(DISTINCT query) AS unique_queries,
    count(DISTINCT username) AS unique_users
FROM
    queries
WHERE
    username LIKE 's%';

CREATE OR REPLACE VIEW v_button_presses AS
SELECT 
    button,
    COUNT(*) AS press_count
FROM 
    messages
    JOIN queries ON messages.query_id = queries.id
WHERE
    username LIKE 's%'
GROUP BY 
    button
ORDER BY 
    button;

CREATE OR REPLACE VIEW v_button_presses_by_user AS
SELECT 
    username,
    button,
    COUNT(*) AS press_count
FROM 
    messages
    JOIN queries ON messages.query_id = queries.id
WHERE
    username LIKE 's%'
GROUP BY 
    username, button
ORDER BY 
    username, button;

CREATE OR REPLACE VIEW v_user_query_counts AS
SELECT 
    username,
    COUNT(*) FILTER (WHERE success) AS success,
    COUNT(DISTINCT query) FILTER (WHERE success) AS unique_success,
    COUNT(messages.id) FILTER (WHERE success) AS success_message,
    COUNT(*) FILTER (WHERE NOT success) AS error,
    COUNT(DISTINCT query) FILTER (WHERE NOT success) AS unique_error,
    COUNT(messages.id) FILTER (WHERE NOT success) AS error_message
FROM 
    queries
    LEFT JOIN messages ON queries.id = messages.query_id
WHERE
    username LIKE 's%'
GROUP BY 
    username
ORDER BY 
    username;

CREATE OR REPLACE VIEW v_feedbacks AS
SELECT 
    button,
    COUNT(*) AS times_pressed,
    COUNT(*) FILTER (WHERE feedback = TRUE) AS positive_feedback,
    COUNT(*) FILTER (WHERE feedback = FALSE) AS negative_feedback
FROM
    messages
    JOIN queries ON messages.query_id = queries.id
WHERE
    username LIKE 's%'
GROUP BY
    button
ORDER BY
    button;
COMMIT;