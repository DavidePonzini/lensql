-- remove cross schema FK, most likely due to contamination
DELETE from query_context_columns WHERE foreign_key_schema IS NOT NULL and schema_name <> foreign_key_schema;

-- remove duplicates, most likely due to contamination
DELETE FROM query_context_columns a USING query_context_columns b
WHERE a.id > b.id
AND a.query_id = b.query_id
AND a.schema_name = b.schema_name
AND a.table_name = b.table_name
AND a.column_name = b.column_name;

-- add unique constraint to prevent future duplicates
ALTER TABLE query_context_columns
ADD CONSTRAINT uq_query_context_columns UNIQUE (query_id, schema_name, table_name, column_name);

-- clean up `"$user", public` schema references
UPDATE queries SET search_path = 'public' WHERE search_path = '"$user", public';

-- clean up escaping issues in search_path
UPDATE queries set search_path = RIGHT(LEFT(search_path, -1), -1) WHERE search_path LIKE '"%"';

-- rename DBMS: 'postgresql' to 'postgres'
UPDATE datasets set dbms = 'postgres' WHERE dbms = 'postgresql';

-- fix incorrect search_path due to dataset initialization
update queries set search_path = 'p_260411' where id between 13692 and 13710;
update queries set search_path = 'unicorsi' where id in (
    16156,
    20886,
    20901,
    20951,
    21266,
    21271,
    23457,
    24713,
    24714,
    24715,
    24716,
    24717,
    24718,
    24719,
    24720,
    28408,
    28493,
    -1
);