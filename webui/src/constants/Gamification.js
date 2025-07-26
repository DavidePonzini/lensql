const Coins = {
    MAX_CHECK_SOLUTION_COST: 5,

    checkSolutionCost: (attempts) => {
        if (attempts === 0)
            return 'Free';

        const cost = Math.min(attempts, Coins.MAX_CHECK_SOLUTION_COST);

        return cost;
    },

    EXERCISE_SOLVED: 100,

    HELP_SUCCESS_DESCRIBE: -1,
    HELP_SUCCESS_EXPLAIN: -3,

    HELP_ERROR_EXPLAIN: -1,
    HELP_ERROR_EXAMPLE: -3,
    HELP_ERROR_LOCATE: -5,
    HELP_ERROR_FIX: -20,

    HELP_FEEDBACK: 5,
};

const Experience = {
    EXERCISE_SOLVED: 1000,
    QUERY_RUN: 1,
    QUERY_RUN_UNIQUE: 10,
    ASK_HELP: 1,
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
    return level >= 0 && level < levelTitles.length
        ? levelTitles[level]
        : `Level ${level}`;
}


function cumulativeXp(level) {
    return Math.floor(100 * level * (level + 1) * (2 * level + 1) / 6);
}

function getXpStats(totalXp) {
    if (totalXp < 0) totalXp = 0;

    let level = 0;
    while (cumulativeXp(level + 1) <= totalXp) {
        level++;
    }

    const xpForCurrentLevel = cumulativeXp(level);
    const xpForNextLevel = cumulativeXp(level + 1);
    const current = totalXp - xpForCurrentLevel;
    const next = xpForNextLevel - xpForCurrentLevel;

    return {
        level,
        current,
        next
    };
}

export { Experience, Coins, getXpStats, getLevelTitle }