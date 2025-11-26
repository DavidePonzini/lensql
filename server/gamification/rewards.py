from .reward import Reward

class Actions:
    '''Actions provide a simple and repeatable reward.'''
    class Query:
        UNIQUE_RUN = Reward('New query executed', experience=25)
        '''Run a query for the first time'''

        RUN = Reward('Query executed', experience=5)
        '''Run a query that has been run before'''

    class Exercise:
        SOLVED = Reward('Exercise solved for the first time', experience=1000, coins=100)
        '''Find the correct solution for the first time'''

        REPEATED = Reward('Solution is correct', experience=10)
        '''Solve an exercise you've already solved (repetition)'''

        @staticmethod
        def check_solution_cost(attempts: int) -> Reward:
            '''Cost for checking a solution'''
            cost = min(attempts, 5)
            return Reward('Checked solution', coins=-cost)

    class Messages:
        HELP_SUCCESS_DESCRIBE = Reward('Interacted with Lens', experience=5, coins=-1)
        HELP_SUCCESS_EXPLAIN = Reward('Interacted with Lens', experience=5, coins=-3)

        HELP_ERROR_EXPLAIN = Reward('Interacted with Lens', experience=5, coins=-1)
        HELP_ERROR_EXAMPLE = Reward('Interacted with Lens', experience=5, coins=-3)
        HELP_ERROR_LOCATE = Reward('Interacted with Lens', experience=5, coins=-5)
        HELP_ERROR_FIX = Reward('Interacted with Lens', experience=5, coins=-10)

        FEEDBACK = Reward('Provided feedback', experience=5, coins=10)

class Badges:
    '''Badges are special rewards that are given for reaching certain milestones. They can only be earned once.'''
    # NOTE: make sure the names here match the ones in `webui/src/locales/*/translations.json` > `gamification.badges`

    CREATE_EXERCISES = {
        1: Reward('create_exercises.1', coins=20),
        5: Reward('create_exercises.5', coins=50),
        10: Reward('create_exercises.10', coins=75),
    }
    '''Create exercises and run at least one query in it'''

    FEEDBACK = {
        1: Reward('feedback.1', coins=10),
        10: Reward('feedback.10', coins=25),
        50: Reward('feedback.50', coins=50),
    }
    '''Give feedback on help messages'''

    QUERIES_UNIQUE = {
        1: Reward('queries_unique.1', coins=5),
        10: Reward('queries_unique.10', coins=10),
        50: Reward('queries_unique.50', coins=25),
        100: Reward('queries_unique.100', coins=50),
        500: Reward('queries_unique.500', coins=50),
        1000: Reward('queries_unique.1000', coins=100),
        2500: Reward('queries_unique.2500', coins=100),
        5000: Reward('queries_unique.5000', coins=100),
        10000: Reward('queries_unique.10000', coins=200),
    }
    '''Run unique queries'''

    EXERCISE_SOLUTIONS = {
        1: Reward('exercise_solutions.1', coins=10),
        5: Reward('exercise_solutions.5', coins=20),
        10: Reward('exercise_solutions.10', coins=50),
    }
    '''Solve exercises'''

    HELP_USAGE = {
        1: Reward('help_usage.1', coins=5),
        10: Reward('help_usage.10', coins=20),
        50: Reward('help_usage.50', coins=50),
        100: Reward('help_usage.100', coins=75),
        500: Reward('help_usage.500', coins=100),
        1000: Reward('help_usage.1000', coins=200),
    }
    '''Use Lens' help'''

    DAILY_USAGE = {
        5: Reward('daily_usage.5', coins=25),
        14: Reward('daily_usage.14', coins=50),
        30: Reward('daily_usage.30', coins=75),
    }
    '''Use LensQL on different days'''

    # TODO
    LEVEL_UP = {
        3: Reward('level_up.3', coins=10),
        5: Reward('level_up.5', coins=25),
        10: Reward('level_up.10', coins=50),
    }
    '''Reach levels'''

    JOIN_DATASET = {
        1: Reward('join_course.1', coins=20)
    }
    '''Join your first course'''
