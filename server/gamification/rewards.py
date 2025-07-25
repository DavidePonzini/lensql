from .reward import Reward

class Actions:
    class Query:
        '''Run a query for the first time'''
        UNIQUE_RUN = Reward('New query executed', experience=10, coins=5)

        '''Run a query that has been run before'''
        RUN = Reward('Query executed', experience=5, coins=2)

    class Exercise:
        '''Find the correct solution for the first time'''
        SOLVED = Reward('Exercise solved for the first time', experience=1000, coins=100)

        '''Solve an exercise you've already solved (repetition)'''
        REPEATED = Reward('Solution is correct', experience=10)

        '''Cost for checking a solution'''
        @staticmethod
        def check_solution_cost(attempts: int) -> Reward:
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
    '''Create exercises and run at least one query in it'''
    CREATE_EXERCISES = {
        1: Reward('Created your first exercise and run a query in it', coins=20),
        5: Reward('Created 5 exercises and run a query in each of them', coins=50),
        10: Reward('Created 10 exercises and run a query in each of them', coins=75),

    }

    '''Give feedback on help messages'''
    FEEDBACK = {
        1: Reward('Provided your first feedback', coins=10),
        10: Reward('Provided feedback 10 times', coins=25),
        50: Reward('Provided feedback 50 times', coins=50),
    }

    '''Run unique queries'''
    QUERIES_UNIQUE = {
        1: Reward('Ran your first query', coins=10),
        10: Reward('Ran 10 different queries', coins=10),
        50: Reward('Ran 50 different queries', coins=25),
        100: Reward('Ran 100 different queries', coins=50),
        500: Reward('Ran 500 different queries', coins=50),
        1000: Reward('Ran 1000 different queries', coins=100),
        2500: Reward('Ran 2500 different queries', coins=100),
        5000: Reward('Ran 5000 different queries', coins=100),
        10000: Reward('Ran 10000 different queries', coins=200),
    }

    '''Solve exercises'''
    EXERCISE_SOLUTIONS = {
        1: Reward('Solved your first exercise', coins=10),
        5: Reward('Solved 5 exercises', coins=20),
        10: Reward('Solved 10 exercises', coins=50),
    }

    '''Use Lens' help'''
    HELP_USAGE = {
        1: Reward('Interacted with Lens for the first time', coins=5),
        10: Reward('Interacted with Lens 10 times', coins=20),
        50: Reward('Interacted with Lens 50 times', coins=50),
        100: Reward('Interacted with Lens 100 times', coins=75),
        500: Reward('Interacted with Lens 500 times', coins=100),
        1000: Reward('Interacted with Lens 1000 times', coins=200),
    }

    '''Use LensQL on different days'''
    DAILY_USAGE = {
        5: Reward('Run a query in 5 different days', coins=25),
        14: Reward('Run a query in 14 different days', coins=50),
        30: Reward('Run a query in 30 different days', coins=50),
    }

    # TODO
    '''Reach levels'''
    LEVEL_UP = {
        3: Reward('Reached level 3', coins=10),
        5: Reward('Reached level 5', coins=25),
        10: Reward('Reached level 10', coins=50),
    }

    '''Join your first course'''
    JOIN_COURSE = {
        1: Reward('Joined your first course', coins=20)
    }
