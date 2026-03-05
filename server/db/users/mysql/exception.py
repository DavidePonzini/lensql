import mysql.connector as mysql

from server.sql.exception import SQLException


class MySQLException(SQLException):
    def __init__(self, exception: mysql.Error):
        message = str(exception.msg) if exception.msg else str(exception)

        lines = message.splitlines()
        description = lines[0] if lines else ''
        traceback = lines[1:] if len(lines) > 1 else []

        super().__init__(
            exception=exception,
            name=type(exception).__name__,
            error_code=exception.errno,
            description=description,
            traceback=traceback
        )