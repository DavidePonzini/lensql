from enum import Enum

class QueryGoal(Enum):
    """Enum representing the goal of a query."""
    UNKNOWN = 'UNKNOWN'             # Not a SELECT query or cannot determine goal
    BUILTIN = 'BUILTIN'             # Builtin query
    SOLUTION = 'SOLUTION'           # Query is the correct solution to an exercise
    FOCUSED = 'FOCUSED'             # Query is a partial solution
    EXPLORATORY = 'EXPLORATORY'     # SELECT * without WHERE/GROUP BY/HAVING, likely exploratory


