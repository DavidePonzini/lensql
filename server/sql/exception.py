from abc import ABC

class SQLException(Exception, ABC):
    '''Custom exception for SQL errors in the database.'''
    def __init__(
            self,
            exception,
            name,
            error_code,
            description: str,
            traceback: list[str]
        ):
        self.exception = exception
        self.name = name
        self.error_code = error_code
        self.description = description
        self.traceback = traceback
    
    def __str__(self):
        return f'{self.name}: {self.description}'
