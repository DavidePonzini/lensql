from enum import Enum

class Coins(Enum):
    EXERCISE_SOLVED = 100

    HELP_SUCCESS_EXPLAIN = -1
    HELP_SUCCESS_DESCRIBE = -3
    HELP_ERROR_EXPLAIN = -3
    HELP_ERROR_EXAMPLE = -3
    HELP_ERROR_LOCATE = -5
    HELP_ERROR_FIX = -20

    HELP_FEEDBACK = 5

# maybe implement it as a function?
# exp = exercises solved * 1000 + queries run * 1 + unique queries run * 10
# this way it can be retroactively calculated
class Experience(Enum):
    EXERCISE_SOLVED = 1000
    QUERY_RUN = 1
    QUERY_RUN_UNIQUE = 10

# Experience grows quadratically with level
# Level 0: 0 XP
# Level 1: 100 XP
# Level 2: 400 XP
# Level 3: 900 XP
# Level 4: 1600 XP
# Level 5: 2500 XP
# ...
def get_level(experience: int) -> int:
    '''Calculate the level based on experience points'''
    level = 0
    base = 100
    total_xp = 0

    while True:
        xp_for_next = base * (level + 1) ** 2
        if experience < total_xp + xp_for_next:
            break
        total_xp += xp_for_next
        level += 1

    return level


def get_experience_for_next_level(level: int) -> int:
    '''Calculate the experience points needed for the next level'''
    base = 100
    return base * (level + 1) ** 2
