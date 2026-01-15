from abc import ABC, abstractmethod

class BuiltinQueries(ABC):
    @staticmethod
    @abstractmethod
    def show_search_path() -> str:
        '''Shows the search path for the database.'''
        pass

    @staticmethod
    @abstractmethod
    def list_users() -> str:
        '''Lists all users in the database.'''
        pass
    
    @staticmethod
    @abstractmethod
    def list_schemas() -> str:
        '''Lists all schemas in the database.'''
        pass

    @staticmethod
    @abstractmethod
    def list_tables() -> str:
        '''Lists tables in the current search_path.'''
        pass

    @staticmethod
    @abstractmethod
    def list_all_tables() -> str:
        '''Lists all tables in the database.'''
        pass

    @staticmethod
    @abstractmethod
    def list_constraints() -> str:
        '''Lists all constraints in the database.'''
        pass

    
class MetadataQueries(ABC):
    @staticmethod
    @abstractmethod
    def get_search_path() -> str:
        '''Returns the current search path for the user.'''
        pass

    @staticmethod
    @abstractmethod
    def get_columns() -> str:
        '''Lists all tables'''
        pass

    @staticmethod
    @abstractmethod
    def get_unique_columns() -> str:
        '''Lists unique columns.'''
        pass
