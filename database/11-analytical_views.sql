BEGIN;

CREATE OR REPLACE VIEW lensql.v_button_presses AS
SELECT 
    button,
    COUNT(*) AS press_count
FROM 
    lensql.buttons
GROUP BY 
    button
ORDER BY 
    button;

CREATE OR REPLACE VIEW lensql.v_button_presses_by_user AS
SELECT 
    username,
    button,
    COUNT(*) AS press_count
FROM 
    lensql.buttons
GROUP BY 
    username, button
ORDER BY 
    username, button;

CREATE OR REPLACE VIEW lensql.v_user_query_counts AS
SELECT 
    username,
    COUNT(*) FILTER (WHERE success) AS success_count,
    COUNT(*) FILTER (WHERE NOT success) AS error_count
FROM 
    lensql.queries
GROUP BY 
    username
ORDER BY 
    username;

COMMIT;