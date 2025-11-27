import { useState } from 'react';
import { useEffect } from 'react';
import { useCallback } from 'react';
import useAuth from '../../hooks/useAuth';

import AchievementBadge from '../../components/AchievementBadge';

function Badges() {
    const { apiRequest } = useAuth();

    const [badges, setBadges] = useState({});

    const fetchBadges = useCallback(async () => {
        const result = await apiRequest('/api/users/badges', 'GET')

        setBadges(result?.data || {});
    }, [apiRequest]);

    useEffect(() => {
        fetchBadges();
    }, [fetchBadges]);

    return (
        <div>
            <div className='row'>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.level_up.name'}
                        description={'gamification.badges.level_up.description'}
                        rank={badges['level_up']?.rank || 0}
                        current={badges['level_up']?.current || 0}
                        next={badges['level_up']?.next || 100}
                        textNext={'gamification.badges.level_up.next'}
                        icon='🚀'
                    />
                </div>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.queries_unique.name'}
                        description={'gamification.badges.queries_unique.description'}
                        rank={badges['queries_unique']?.rank || 0}
                        current={badges['queries_unique']?.current || 0}
                        next={badges['queries_unique']?.next || 50}
                        textNext={'gamification.badges.queries_unique.next'}
                        icon='📚'
                    />
                </div>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.daily_usage.name'}
                        description={'gamification.badges.daily_usage.description'}
                        rank={badges['daily_usage']?.rank || 0}
                        current={badges['daily_usage']?.current || 0}
                        next={badges['daily_usage']?.next || 60}
                        textNext={'gamification.badges.daily_usage.next'}
                        icon='📅'
                    />
                </div>
            </div>

            <div className='row mt-4'>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.exercise_solutions.name'}
                        description={'gamification.badges.exercise_solutions.description'}
                        rank={badges['exercise_solutions']?.rank || 0}
                        current={badges['exercise_solutions']?.current || 0}
                        next={badges['exercise_solutions']?.next || 80}
                        textNext={'gamification.badges.exercise_solutions.next'}
                        icon='✅'
                    />
                </div>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.create_exercises.name'}
                        description={'gamification.badges.create_exercises.description'}
                        rank={badges['create_exercises']?.rank || 0}
                        current={badges['create_exercises']?.current || 0}
                        next={badges['create_exercises']?.next || 100}
                        textNext={'gamification.badges.create_exercises.next'}
                        icon='📝'
                    />
                </div>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.join_dataset.name'}
                        description={'gamification.badges.join_dataset.description'}
                        rank={badges['join_dataset']?.rank || 0}
                        current={badges['join_dataset']?.current || 0}
                        next={badges['join_dataset']?.next || 10}
                        textNext={'gamification.badges.join_dataset.next'}
                        icon='👋'
                    />
                </div>
            </div>

            <div className='row mt-4'>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.help_usage.name'}
                        description={'gamification.badges.help_usage.description'}
                        rank={badges['help_usage']?.rank || 0}
                        current={badges['help_usage']?.current || 0}
                        next={badges['help_usage']?.next || 150}
                        textNext={'gamification.badges.help_usage.next'}
                        icon='🤖'
                    />
                </div>
                <div className='col-sm-4'>
                    <AchievementBadge
                        name={'gamification.badges.feedback.name'}
                        description={'gamification.badges.feedback.description'}
                        rank={badges['feedback']?.rank || 0}
                        current={badges['feedback']?.current || 0}
                        next={badges['feedback']?.next || 30}
                        textNext={'gamification.badges.feedback.next'}
                        icon='💬'
                    />
                </div>
            </div>
        </div>
    )
}

export default Badges;