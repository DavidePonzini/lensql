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
# Level 0:    0 XP  |   0
# Level 1:  100 XP  | 100
# Level 2:  400 XP  | 500
# Level 3:  900 XP  | 1400
# Level 4: 1600 XP  | 3000
# Level 5: 2500 XP  | 5500
# ...
def xp_to_level(total_xp):
    def cumulative_xp(level):
        return 100 * level * (level + 1) * (2 * level + 1) // 6

    # Find level by incrementing until XP would exceed total_xp
    level = 0
    while cumulative_xp(level + 1) <= total_xp:
        level += 1

    xp_for_current_level = cumulative_xp(level)
    xp_for_next_level = cumulative_xp(level + 1)
    current_level_xp = total_xp - xp_for_current_level

    return {
        'level': level,
        'current': current_level_xp,
        'next': xp_for_next_level - xp_for_current_level
    }
