# List of commands: https://www.postgresql.org/docs/current/sql-commands.html

allowed_types = {
    'ABORT', # — abort the current transaction
    'ALTER',
    # ANALYZE — collect statistics about a database
    'BEGIN', # — start a transaction block
    'CALL', # — invoke a procedure
    # CHECKPOINT — force a write-ahead log checkpoint
    # CLOSE — close a cursor
    'CLUSTER', # — cluster a table according to an index
    # COMMENT — define or change the comment of an object
    'COMMIT', # — commit the current transaction
    'COPY', # — copy data between a file and a table
    'CREATE',
    # DEALLOCATE — deallocate a prepared statement
    # DECLARE — define a cursor
    'DELETE', # — delete rows of a table
    # DISCARD — discard session state
    'DO', # — execute an anonymous code block
    'DROP',
    'END', # — commit the current transaction
    # EXECUTE — execute a prepared statement
    'EXPLAIN', # — show the execution plan of a statement
    # FETCH — retrieve rows from a query using a cursor
    'GRANT', # — define access privileges
    # IMPORT FOREIGN SCHEMA — import table definitions from a foreign server
    'INSERT', # — create new rows in a table
    # LISTEN — listen for a notification
    # LOAD — load a shared library file
    # LOCK — lock a table
    # MERGE — conditionally insert, update, or delete rows of a table
    # MOVE — position a cursor
    # NOTIFY — generate a notification
    # PREPARE — prepare a statement for execution
    # PREPARE TRANSACTION — prepare the current transaction for two-phase commit
    # REASSIGN OWNED — change the ownership of database objects owned by a database role
    # REFRESH MATERIALIZED VIEW — replace the contents of a materialized view
    'REINDEX', # — rebuild indexes
    # RELEASE SAVEPOINT — release a previously defined savepoint
    'RESET', # — restore the value of a run-time parameter to the default value
    'REVOKE', # — remove access privileges
    'ROLLBACK', # — abort the current transaction
    'SAVEPOINT', # — define a new savepoint within the current transaction
    # SECURITY LABEL — define or change a security label applied to an object
    'SELECT', # — retrieve rows from a table or view
    'SET', # — change a run-time parameter
    'SHOW', # — show the value of a run-time parameter
    'START', # TRANSACTION — start a transaction block
    'TRUNCATE', # — empty a table or set of tables
    # UNLISTEN — stop listening for a notification
    'UPDATE', # — update rows of a table
    # VACUUM — garbage-collect and optionally analyze a database
    # VALUES — compute a set of rows

    # manually added
    'WITH',
}
