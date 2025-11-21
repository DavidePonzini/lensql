BEGIN;

SET search_path TO lensql;

INSERT INTO learning_objectives(id) VALUES
-- SELECT
    ('Simple Select'),
    ('Single condition'),
    ('Distinct'),
    ('Aggregate functions'),
    ('Subquery in SELECT'),
    ('Case statements'),
    ('String functions'),
    ('Date functions'),
    ('Numeric functions'),
    ('Window functions'),
-- FROM
    ('Simple join'),
    ('Self join'),
    ('Left join'),
    ('Right join'),
    ('Full outer join'),
    ('Subquery in FROM'),
-- WHERE
    ('Multiple conditions'),
    ('Subquery in WHERE'),
    ('Correlated subqueries'),
-- GROUP BY
    ('Group by'),
-- HAVING
    ('Group by with conditions'),
-- ORDER BY
    ('Order by'),
-- LIMIT
    ('Limit and offset'),
-- OTHER
    ('Union'),
    ('Intersect'),
    ('Except')
ON CONFLICT (id) DO NOTHING;

COMMIT;