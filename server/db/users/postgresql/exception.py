import psycopg2 as pg

from server.sql.exception import SQLException

class PostgresqlException(SQLException):
    def __init__(self, exception: pg.Error):
        message = str(exception.args[0]) if exception.args else ''
        description = message.splitlines()[0]
        traceback = message.splitlines()[1:]

        super().__init__(
            exception=exception,
            name=type(exception).__name__,
            error_code=exception.pgcode,
            description=description,
            traceback=traceback
        )
