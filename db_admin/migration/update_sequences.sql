BEGIN;

SET search_path TO lensql;

SELECT setval(
    'exercises_id_seq',
    COALESCE((SELECT MAX(id) FROM exercises), 0) + 1,
    false
);

SELECT setval(
    'has_error_id_seq',
    COALESCE((SELECT MAX(id) FROM has_error), 0) + 1,
    false
);

SELECT setval(
    'messages_id_seq',
    COALESCE((SELECT MAX(id) FROM messages), 0) + 1,
    false
);

SELECT setval(
    'queries_id_seq',
    COALESCE((SELECT MAX(id) FROM queries), 0) + 1,
    false
);

SELECT setval(
    'query_batches_id_seq',
    COALESCE((SELECT MAX(id) FROM query_batches), 0) + 1,
    false
);

SELECT setval(
    'query_context_columns_id_seq',
    COALESCE((SELECT MAX(id) FROM query_context_columns), 0) + 1,
    false
);

SELECT setval(
    'query_context_columns_unique_id_seq',
    COALESCE((SELECT MAX(id) FROM query_context_columns_unique), 0) + 1,
    false
);

COMMIT;
