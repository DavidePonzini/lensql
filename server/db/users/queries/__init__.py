from . import builtin
from ..connection import get_connection
from server.sql import SQLCode, SQLException, QueryResult, QueryResultDataset, QueryResultError, QueryResultMessage, Column

import pandas as pd
from typing import Iterable

from dav_tools import messages

def execute(username: str, query_str: str, *, strip_comments: bool = True) -> Iterable[QueryResult]:
    '''
    Executes the given SQL queries and returns the results.
    The queries will be separated into individual statements.

    Parameters:
        username (str): The username of the database user.
        query_str (str): The SQL query string to execute. The query string can contain multiple SQL statements separated by semicolons.
    Returns:
        Iterable[QueryResult]: An iterable of QueryResult objects.
    '''

    for statement in SQLCode(query_str).split():
    
        # NOTE: do not `strip_comments` from the SQL code for very large queries
        #   as it takes the server too much time to parse the SQL code,
        #   causing a timeout error in the client.
        if strip_comments:
            statement = statement.strip_comments()

        try:
            conn = get_connection(username)
            with conn.cursor() as cur:
                cur.execute(statement.query)
                    
                if cur.description:  # Check if the query has a result set
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]

                    yield QueryResultDataset(
                        result=pd.DataFrame(rows, columns=columns),
                        columns=[Column(name=col.name, data_type=col.type_code) for col in cur.description] if cur.description else [],
                        query=statement.query,
                        query_type=statement.query_type,
                        query_goal=statement.query_goal,
                        notices=conn.notices)
                    continue

                
                # No result set, return message status 
                yield QueryResultMessage(
                    message=f'{cur.statusmessage}',
                    query=statement.query,
                    query_type=statement.query_type,
                    query_goal=statement.query_goal,
                    notices=conn.notices)

            conn.update_last_operation_ts()
        except Exception as e:
            try:
                conn.rollback()
                conn.update_last_operation_ts()
            except Exception as e:
                messages.error(f"Error rolling back connection for user {username}: {e}")
            yield QueryResultError(
                exception=SQLException(e),
                query=statement.query,
                query_type=statement.query_type,
                query_goal=statement.query_goal,
                notices=conn.notices)


