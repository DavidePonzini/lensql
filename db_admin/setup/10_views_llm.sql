BEGIN;

SET search_path to lensql;

CREATE OR REPLACE VIEW v_button_presses AS
SELECT 
    button,
    COUNT(*) AS press_count
FROM 
    messages m
GROUP BY 
    button
ORDER BY 
    press_count DESC;

CREATE OR REPLACE VIEW v_button_presses_by_user AS
SELECT 
    qb.username,
    m.button,
    COUNT(*) AS press_count
FROM 
    messages m
    JOIN queries q ON m.query_id = q.id
    JOIN query_batches qb ON q.batch_id = qb.id
GROUP BY 
    qb.username, m.button
ORDER BY 
    qb.username, press_count DESC;

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