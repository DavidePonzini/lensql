from dav_tools import database
from .connection import db, SCHEMA

def get_info(username: str) -> dict:
    '''Get general information about a user'''

    query = database.sql.SQL(
    '''
        SELECT
            is_admin,
            is_teacher
        FROM
            {schema}.v_user_info
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    if len(result) == 0:
        return None
    return {
        'username': username,
        'is_admin': result[0][0],
        'is_teacher': result[0][1],
    }

def get_learning_stats(username: str) -> dict:
    '''Get learning statistics for a user'''

    statement_queries = database.sql.SQL(
    '''
    SELECT
        q.query_type,
        COUNT(q.id) AS queries,
        COUNT(DISTINCT q.query) AS queries_d,
        SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
    FROM
        {schema}.queries q
        JOIN {schema}.query_batches qb ON qb.id = q.batch_id
    WHERE
        qb.username = {username}
        AND q.query_type <> 'BUILTIN'
    GROUP BY
        q.query_type
    ORDER BY
        -- q.query_type;
        queries DESC;
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result_queries = db.execute_and_fetch(statement_queries, {
        'username': username
    })

    statement_messages = database.sql.SQL(
    '''
    SELECT
        COUNT(button) AS count,
        SUM(CASE WHEN query_type = 'SELECT' THEN 1 ELSE 0 END) AS select_count,
        SUM(CASE WHEN success THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN feedback IS NOT NULL THEN 1 ELSE 0 END) AS feedback_count
    FROM
        {schema}.messages m
        JOIN {schema}.queries q ON q.id = m.query_id
        JOIN {schema}.query_batches qb ON qb.id = q.batch_id
    WHERE
        qb.username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result_messages = db.execute_and_fetch(statement_messages, {
        'username': username
    })[0]

    return {
        'queries': sum(row[1] for row in result_queries),
        'queries_d': sum(row[2] for row in result_queries),
        'success_rate': sum(row[3] for row in result_queries) / sum(row[1] for row in result_queries) if sum(row[1] for row in result_queries) > 0 else 0,
        'success_rate_select': sum(row[3] for row in result_queries if row[0] == 'SELECT') / sum(row[1] for row in result_queries if row[0] == 'SELECT') if sum(row[1] for row in result_queries if row[0] == 'SELECT') > 0 else 0,
        'query_types': [
            {
                'type': row[0],
                'count': row[1],
                'count_d': row[2],
                'success': row[3]
            } for row in result_queries
        ],
        'messages': result_messages[0],
        'messages_select': result_messages[1],
        'messages_success': result_messages[2],
        'messages_error': result_messages[0] - result_messages[2],
        'messages_feedback_perc': result_messages[3] / result_messages[0] if result_messages[0] > 0 else 0,
    }