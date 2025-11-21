BEGIN;

SET search_path TO lensql;

-- Load a dataset from a file on disk ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION load_dataset(dataset_id TEXT, dataset_name TEXT, file_path TEXT)
RETURNS VOID AS $$
DECLARE
    contents TEXT;
BEGIN
    -- Read file contents from Docker build context (mounted into /datasets)
    SELECT pg_read_file(file_path) INTO contents;

    -- Insert or update dataset row
    INSERT INTO datasets(id, name, dataset)
    VALUES (dataset_id, dataset_name, contents)
    ON CONFLICT (id)
    DO UPDATE SET
        name = EXCLUDED.name,
        dataset = EXCLUDED.dataset;

END;
$$ LANGUAGE plpgsql;

-- Load default datasets -------------------------------------------------------------------------------
SELECT load_dataset('_EXPLORE', 'Explore SQL', '/datasets/explore.sql');
SELECT load_dataset('_WELCOME_MIEDEMA', 'Sample Dataset: Miedema', '/datasets/miedema.sql');

COMMIT;