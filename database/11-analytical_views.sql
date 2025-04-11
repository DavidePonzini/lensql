BEGIN;

SET search_path to lensql;

CREATE OR REPLACE VIEW v_button_presses AS
SELECT 
    button,
    COUNT(*) AS press_count
FROM 
    messages
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
GROUP BY 
    username, button
ORDER BY 
    username, button;

CREATE OR REPLACE VIEW v_user_query_counts AS
SELECT 
    username,
    COUNT(*) FILTER (WHERE success) AS success_count,
    COUNT(*) FILTER (WHERE NOT success) AS error_count
FROM 
    queries
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
GROUP BY
    button
ORDER BY
    button;
COMMIT;