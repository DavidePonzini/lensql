class SQLException:
    def __init__(self, exception: Exception):
        self.exception = exception

        self.name = type(self.exception).__name__

        message = str(self.exception.args[0]) if self.exception.args else ''
        self.description = message.splitlines()[0]
        self.traceback = message.splitlines()[1:]
    
    def __str__(self):
        return f'{self.name}: {self.description}'