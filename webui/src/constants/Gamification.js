const Coins = {
    MAX_CHECK_SOLUTION_COST: 5,

    HELP_SUCCESS_DESCRIBE: -1,
    HELP_SUCCESS_EXPLAIN: -3,

    HELP_ERROR_EXPLAIN: -1,
    HELP_ERROR_EXAMPLE: -3,
    HELP_ERROR_LOCATE: -5,
    HELP_ERROR_FIX: -10,

    HELP_FEEDBACK: 10,

    EXERCISE_SOLVED: 100,

    checkSolutionCost: (attempts) => {
        if (attempts === 0) return 0;
        return -Math.min(attempts, Coins.MAX_CHECK_SOLUTION_COST);
    },
};

const Experience = {
    QUERY_RUN: 5,
    QUERY_RUN_UNIQUE: 25,
    EXERCISE_SOLVED: 1000,
    EXERCISE_REPEATED: 10,
    HELP: 5,
    FEEDBACK: 5,
};

const expActions = [
    { label: 'Solve exercises', value: '+1000 XP', positive: true },
    { label: 'Run queries', value: '+5 XP each', positive: true },
    { label: 'Try new, unique queries', value: '+25 XP each', positive: true },
    { label: 'Interact with Lens', value: '+5 XP', positive: true },
    { label: 'Give feedback on Lens’ help', value: '+5 XP', positive: true },
    { label: 'Unlock achievements', value: 'variable amounts', positive: true },
];

const coinActions = [
    { label: 'Check if a solution is correct', value: 'from 0 to -5 coins', positive: false },
    { label: 'Ask Lens for help', value: 'from 0 to -10 coins', positive: false },
    { label: 'Give feedback on Lens’ help', value: '+10 coins', positive: true },
    { label: 'Solve exercises', value: '+100 coins', positive: true },
    { label: 'Unlock achievements', value: 'variable amounts', positive: true },
];

const badges = {
    CREATE_EXERCISES: {
        1: { label: 'Created your first exercise and run a query in it', coins: 20 },
        5: { label: 'Created 5 exercises and run a query in each of them', coins: 50 },
        10: { label: 'Created 10 exercises and run a query in each of them', coins: 75 }
    },
    FEEDBACK: {
        1: { label: 'Provided your first feedback', coins: 10 },
        10: { label: 'Provided feedback 10 times', coins: 25 },
        50: { label: 'Provided feedback 50 times', coins: 50 }
    },
    QUERIES_UNIQUE: {
        1: { label: 'Ran your first query', coins: 5 },
        10: { label: 'Ran 10 different queries', coins: 10 },
        50: { label: 'Ran 50 different queries', coins: 25 },
        100: { label: 'Ran 100 different queries', coins: 50 },
        500: { label: 'Ran 500 different queries', coins: 50 },
        1000: { label: 'Ran 1000 different queries', coins: 100 },
        2500: { label: 'Ran 2500 different queries', coins: 100 },
        5000: { label: 'Ran 5000 different queries', coins: 100 },
        10000: { label: 'Ran 10000 different queries', coins: 200 }
    },
    EXERCISE_SOLUTIONS: {
        1: { label: 'Solved your first exercise', coins: 10 },
        5: { label: 'Solved 5 exercises', coins: 20 },
        10: { label: 'Solved 10 exercises', coins: 50 }
    },
    HELP_USAGE: {
        1: { label: 'Interacted with Lens for the first time', coins: 5 },
        10: { label: 'Interacted with Lens 10 times', coins: 20 },
        50: { label: 'Interacted with Lens 50 times', coins: 50 },
        100: { label: 'Interacted with Lens 100 times', coins: 75 },
        500: { label: 'Interacted with Lens 500 times', coins: 100 },
        1000: { label: 'Interacted with Lens 1000 times', coins: 200 }
    },
    DAILY_USAGE: {
        5: { label: 'Run a query in 5 different days', coins: 25 },
        14: { label: 'Run a query in 14 different days', coins: 50 },
        30: { label: 'Run a query in 30 different days', coins: 75 }
    },
    LEVEL_UP: {
        3: { label: 'Reached level 3', coins: 10 },
        5: { label: 'Reached level 5', coins: 25 },
        10: { label: 'Reached level 10', coins: 50 }
    },
    JOIN_COURSE: {
        1: { label: 'Joined your first course', coins: 20 }
    }
};

const levelTitles = [
    'Curious Beginner',
    'Logical Thinker',
    'Query Novice',
    'Pattern Seeker',
    'Relational Explorer',
    'Intentional Analyst',
    'Data Interpreter',
    'Insight Builder',
    'Structured Thinker',
    'Query Architect'
];

function getLevelTitle(level) {
    return level >= 0 && level < levelTitles.length ? levelTitles[level] : `Level ${level}`;
}

function cumulativeXp(level) {
    return Math.floor(100 * level * (level + 1) * (2 * level + 1) / 6);
}

function getXpStats(totalXp) {
    if (totalXp < 0) totalXp = 0;
    let level = 0;
    while (cumulativeXp(level + 1) <= totalXp) level++;

    const xpForCurrent = cumulativeXp(level);
    const xpForNext = cumulativeXp(level + 1);
    return {
        level,
        current: totalXp - xpForCurrent,
        next: xpForNext - xpForCurrent
    };
}

export { Coins, Experience, expActions, coinActions, badges, getXpStats, getLevelTitle };
