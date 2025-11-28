import { useTranslation } from 'react-i18next';

function useGamificationData() {
    const { t } = useTranslation();

    const Coins = {
        MAX_CHECK_SOLUTION_COST: 5,

        HELP_SUCCESS_DESCRIBE: -1,
        HELP_SUCCESS_EXPLAIN: -3,
        HELP_SUCCESS_CHECK_ERRORS: -10,

        HELP_ERROR_EXPLAIN: -1,
        HELP_ERROR_EXAMPLE: -3,
        HELP_ERROR_LOCATE: -5,
        HELP_ERROR_FIX: -10,

        HELP_FEEDBACK: 10,

        EXERCISE_SOLVED: 100,

        getCheckSolutionCost: (attempts) => {
            if (attempts === 0)
                return 0;

            return Math.min(attempts, Coins.MAX_CHECK_SOLUTION_COST);
        }
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
        { label: t('gamification.actions.solve_exercises.label'), value: t('gamification.actions.solve_exercises.xp'), positive: true },
        { label: t('gamification.actions.run_queries.label'), value: t('gamification.actions.run_queries.xp'), positive: true },
        { label: t('gamification.actions.try_unique_queries.label'), value: t('gamification.actions.try_unique_queries.xp'), positive: true },
        { label: t('gamification.actions.interact_with_lens.label'), value: t('gamification.actions.interact_with_lens.xp'), positive: true },
        { label: t('gamification.actions.feedback_on_lens.label'), value: t('gamification.actions.feedback_on_lens.xp'), positive: true },
        { label: t('gamification.actions.achievements.label'), value: t('gamification.actions.achievements.xp'), positive: true },
    ];

    const coinActions = [
        { label: t('gamification.actions.check_solution.label'), value: t('gamification.actions.check_solution.coins'), positive: false },
        { label: t('gamification.actions.ask_lens.label'), value: t('gamification.actions.ask_lens.coins'), positive: false },
        { label: t('gamification.actions.feedback_on_lens.label'), value: t('gamification.actions.feedback_on_lens.coins'), positive: true },
        { label: t('gamification.actions.solve_exercises.label'), value: t('gamification.actions.solve_exercises.coins'), positive: true },
        { label: t('gamification.actions.achievements.label'), value: t('gamification.actions.achievements.coins'), positive: true },
    ];

    const levelTitles = Array.from({ length: 10 }, (_, i) => t(`gamification.levels.${i}`));

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
        while (cumulativeXp(level + 1) <= totalXp) level++;

        const xpForCurrent = cumulativeXp(level);
        const xpForNext = cumulativeXp(level + 1);
        return {
            level,
            current: totalXp - xpForCurrent,
            next: xpForNext - xpForCurrent
        };
    }

    return {
        Coins,
        Experience,
        expActions,
        coinActions,
        getLevelTitle,
        getXpStats
    };
}

export default useGamificationData;
