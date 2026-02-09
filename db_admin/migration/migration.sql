BEGIN;

INSERT INTO lensql.users(
    username,
    password_hash,
    school,
    is_active,
    is_teacher,
    is_admin,
    registration_ts,
    experience,
    coins,
    can_use_ai
) SELECT 
    username,
    password_hash,
    school,
    is_active,
    is_teacher,
    is_admin,
    registration_ts,
    experience,
    coins,
    can_use_ai
FROM users;

INSERT INTO lensql.badges(
    username,
    badge,
    ts
) SELECT 
    username,
    badge,
    ts
FROM badges;

INSERT INTO lensql.user_unique_queries(
    username,
    query_hash
) SELECT 
    username,
    query_hash
FROM user_unique_queries;

INSERT INTO lensql.datasets(
    id,
    name,
    description,
    dataset,
    domain
) SELECT 
    id,
    name,
    description,
    dataset,
    domain
FROM datasets;

INSERT INTO lensql.dataset_members(
    username,
    dataset_id,
    is_active,
    is_owner,
    joined_ts
) SELECT 
    username,
    dataset_id,
    is_active,
    is_owner,
    joined_ts
FROM dataset_members;

INSERT INTO lensql.errors(
    id,
    category,
    subcategory,
    error
) SELECT 
    id,
    category,
    subcategory,
    error
FROM errors;

INSERT INTO lensql.exercises(
    id,
    dataset_id,
    is_hidden,
    title,
    request,
    solutions,
    search_path,
    created_by,
    created_ts,
    generation_difficulty,
    generation_error
) SELECT 
    id,
    dataset_id,
    is_hidden,
    title,
    request,
    solutions,
    search_path,
    created_by,
    created_ts,
    generation_difficulty,
    generation_error
FROM exercises;

INSERT INTO lensql.learning_objectives(
    id
) SELECT 
    id
FROM learning_objectives;

INSERT INTO lensql.has_learning_objective(
    exercise_id,
    objective_id
) SELECT 
    exercise_id,
    objective_id
FROM has_learning_objective;

INSERT INTO lensql.query_batches(
    id,
    username,
    ts,
    exercise_id
) SELECT 
    id,
    username,
    ts,
    exercise_id
FROM query_batches;

INSERT INTO lensql.queries(
    id,
    batch_id,
    query,
    search_path,
    success,
    result,
    query_type,
    query_goal,
    ts
) SELECT 
    id,
    batch_id,
    query,
    search_path,
    success,
    result,
    query_type,
    query_goal,
    ts
FROM queries;

INSERT INTO lensql.exercise_solutions(
    id,
    is_correct,
    solution_ts
) SELECT 
    id,
    is_correct,
    solution_ts
FROM exercise_solutions;

INSERT INTO lensql.query_context_columns(
    id,
    query_id,
    schema_name,
    table_name,
    column_name,
    column_type,
    numeric_precision,
    numeric_scale,
    foreign_key_schema,
    foreign_key_table,
    foreign_key_column,
    is_nullable
) SELECT 
    id,
    query_id,
    schema_name,
    table_name,
    column_name,
    column_type,
    numeric_precision,
    numeric_scale,
    foreign_key_schema,
    foreign_key_table,
    foreign_key_column,
    is_nullable
FROM query_context_columns;

INSERT INTO lensql.query_context_columns_unique(
    id,
    query_id,
    schema_name,
    table_name,
    constraint_type,
    columns
) SELECT 
    id,
    query_id,
    schema_name,
    table_name,
    constraint_type,
    columns
FROM query_context_columns_unique;

INSERT INTO lensql.has_error(
    id,
    query_id,
    error_id,
    details
) SELECT 
    id,
    query_id,
    error_id,
    details
FROM has_error;

INSERT INTO lensql.messages(
    id,
    query_id,
    answer,
    button,
    msg_idx,
    ts,
    feedback,
    feedback_ts
) SELECT 
    id,
    query_id,
    answer,
    button,
    msg_idx,
    ts,
    feedback,
    feedback_ts
FROM messages;

COMMIT;