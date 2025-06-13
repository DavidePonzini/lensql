from typing import Any

class Column:
    '''Represents a column in a SQL query result.'''
    def __init__(self, name: str, data_type: Any):
        self.name = name
        self.data_type = data_type

    def __repr__(self):
        return f'Column(name="{self.name}", data_type="{self.data_type}")'
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Column):
            return False
        return self.name == other.name and self.data_type == other.data_type

