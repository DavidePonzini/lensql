function UserLevelTitle({ level }) {
    function getLevelTitle(level) {
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

        return level >= 0 && level < levelTitles.length
            ? levelTitles[level]
            : `Level ${level}`;
    }

    const title = getLevelTitle(level);

    return (
        <span>
            {level} <i>({title})</i>
        </span>
    );
}

export default UserLevelTitle;
