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