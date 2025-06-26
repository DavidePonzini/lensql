BEGIN;

SET search_path TO lensql;

INSERT INTO learning_objectives(objective, description) VALUES
-- SELECT
    ('Simple Select', 'Write a simple SELECT statement to retrieve data from a single table.'),
    ('Single condition', 'Write queries that filter results based on a single condition.'),
    ('Distinct', 'Use the DISTINCT keyword to eliminate duplicate rows from query results.'),
    ('Aggregate functions', 'Use aggregate functions like COUNT, SUM, AVG, MIN, and MAX to summarize data.'),
    ('Subquery in SELECT', 'Write queries that include subqueries in the SELECT clause.'),
    ('Case statements', 'Use CASE statements to create conditional logic within queries.'),
    ('String functions', 'Apply string functions to manipulate text data in queries.'),
    ('Date functions', 'Use date functions to manipulate and format date and time data in queries.'),
    ('Numeric functions', 'Apply numeric functions to perform calculations on numeric data in queries.'),
    ('Window functions', 'Use window functions to perform calculations across a set of rows related to the current row.'),
-- FROM
    ('Simple join', 'Write queries that involve a simple join between two tables to retrieve related data.'),
    ('Self join', 'Write queries that involve self-joins to compare rows within the same table.'),
    ('Left join', 'Write queries that use LEFT JOIN to retrieve all rows from one table and matching rows from another.'),
    ('Right join', 'Write queries that use RIGHT JOIN to retrieve all rows from one table and matching rows from another.'),
    ('Full outer join', 'Use FULL OUTER JOIN to retrieve all rows when there is a match in either table.'),
    ('Subquery in FROM', 'Utilize subqueries in the FROM clause to create derived tables.'),
-- WHERE
    ('Multiple conditions', 'Use logical operators to filter results based on multiple conditions.'),
    ('Subquery in WHERE', 'Use subqueries in the WHERE clause to filter results based on related data.'),
    ('Correlated subqueries', 'Write correlated subqueries that reference columns from the outer query.'),
-- GROUP BY
    ('Group by', 'Group results using the GROUP BY clause to aggregate data based on specific columns.'),
-- HAVING
    ('Group by with conditions', 'Use the HAVING clause to filter grouped results based on aggregate conditions.'),
-- ORDER BY
    ('Order by', 'Sort query results using the ORDER BY clause.'),
-- LIMIT
    ('Limit and offset', 'Use LIMIT and OFFSET to control the number of rows returned by a query.'),
-- OTHER
    ('Union', 'Combine results from multiple queries using the UNION operator.'),
    ('Intersect', 'Retrieve common results from multiple queries using the INTERSECT operator.'),
    ('Except', 'Use the EXCEPT operator to find results in one query that are not in another.')
    
    
    ON CONFLICT (objective) DO NOTHING;

COMMIT;