from enum import Enum

class QueryGoal(Enum):
    """Enum representing the goal of a query."""
    UNKNOWN = 'UNKNOWN'
    BUILTIN = 'Builtin query'
    SOLUTION = 'Query is the correct solution to an exercise'
    FOCUSED = 'Query is a partial solution'
    EXPLORATORY = 'SELECT *'


