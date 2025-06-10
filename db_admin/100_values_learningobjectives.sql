BEGIN;

SET search_path TO lensql;

INSERT INTO learning_objectives(objective, description) VALUES
    ('Simple Select', 'Write a simple SELECT statement to retrieve data from a single table.'),
    ('Select with Where', 'Use the WHERE clause to filter results based on specific conditions.'),
    ('Select with Order By', 'Sort the results of a SELECT statement using the ORDER BY clause.'),
    ('Select with Group By', 'Group results using the GROUP BY clause and apply aggregate functions.'),
    ('Select with Join', 'Combine rows from two or more tables based on related columns using JOINs.'),
    ('Subqueries', 'Use subqueries to perform operations that require nested queries.'),
    ('Set Operations', 'Utilize set operations like UNION, INTERSECT, and EXCEPT to combine results from multiple queries.'),
    ('Data Manipulation', 'Insert, update, and delete data in tables using INSERT, UPDATE, and DELETE statements.'),
    ('Functions and Expressions', 'Apply built-in functions and expressions to manipulate data in queries.'),
    ('Advanced Joins', 'Explore advanced join techniques such as LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN.')
    
    ON CONFLICT (objective) DO NOTHING;

COMMIT;