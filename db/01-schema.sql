DROP SCHEMA IF EXISTS sql_collection CASCADE;
CREATE SCHEMA sql_collection;

GRANT ALL PRIVILEGES ON SCHEMA sql_collection TO jupyter_admin;
GRANT USAGE ON SCHEMA sql_collection TO jupyter_user;
GRANT SELECT ON ALL TABLES IN SCHEMA sql_collection TO jupyter_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA sql_collection GRANT SELECT ON TABLES TO jupyter_user;
