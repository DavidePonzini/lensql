-- Apply once to an existing installation, before deploying the updated application.
BEGIN;
ALTER TABLE lensql.users ADD COLUMN ai_generation_credits INTEGER NOT NULL DEFAULT 0
    CHECK (ai_generation_credits >= 0);
ALTER TABLE lensql.datasets RENAME TO activities;
ALTER TABLE lensql.activities RENAME COLUMN dataset TO activity;
ALTER TABLE lensql.dataset_members RENAME TO activity_members;
ALTER TABLE lensql.activity_members RENAME COLUMN dataset_id TO activity_id;
ALTER TABLE lensql.exercises RENAME COLUMN dataset_id TO activity_id;
-- Views retain their dependencies through table/column renames. Recreate them below
-- to update their exposed column names and definitions.
DO $$
DECLARE item RECORD;
BEGIN
    FOR item IN
        SELECT c.relname, a.attname FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid
        WHERE n.nspname = 'lensql' AND c.relkind = 'v'
            AND a.attnum > 0 AND NOT a.attisdropped AND a.attname LIKE '%dataset%'
    LOOP
        EXECUTE format('ALTER VIEW lensql.%I RENAME COLUMN %I TO %I',
            item.relname, item.attname, replace(item.attname, 'dataset', 'activity'));
    END LOOP;
    FOR item IN
        SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'lensql' AND c.relkind = 'v' AND c.relname LIKE '%dataset%'
    LOOP
        EXECUTE format('ALTER VIEW lensql.%I RENAME TO %I',
            item.relname, replace(item.relname, 'dataset', 'activity'));
    END LOOP;
END $$;
COMMIT;
