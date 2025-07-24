import { useEffect, useState } from 'react';
import useAuth from '../../hooks/useAuth';
import LevelTitle from './LevelTitle';
import { Coins, Experience } from '../../constants/Gamification';

function Profile() {
    const expActions = [
        { label: 'Solving exercises', value: `+${Experience.EXERCISE_SOLVED} XP` },
        { label: 'Running queries', value: `+${Experience.QUERY_RUN} XP each` },
        { label: 'Trying new, unique queries', value: `+${Experience.QUERY_RUN_UNIQUE} XP each` },
        { label: 'Interacting with Lens', value: `+${Experience.ASK_HELP} XP` },
    ];

    const coinActions = [
        { label: 'Ask Lens for help', value: `from ${Math.max(...Object.values(Coins).filter(v => v < 0))} to ${Math.min(...Object.values(Coins).filter(v => v < 0))} coins` },
        { label: 'Give feedback on Lens’ help', value: `+${Coins.HELP_FEEDBACK} coins` },
    ];

    const { apiRequest, userInfo } = useAuth();
    const [queriesCount, setQueriesCount] = useState(0);

    useEffect(() => {
        async function fetchProfileData() {
            const response = await apiRequest('/api/users/stats/unique_queries', 'GET');
            setQueriesCount(response.data);
        }

        fetchProfileData();
    }, [apiRequest]);

    const username = userInfo?.username || 'user';
    const xp = userInfo?.xp || 0;
    const xpToNext = userInfo?.xpToNextLevel || 0;
    const coins = userInfo?.coins || 0;
    const level = userInfo?.level || 0;

    const welcomeMessage =
        queriesCount > 100
            ? "Here's a look at your SQL progress — keep going strong!"
            : "Here's a look at your SQL progress";

    return (
        <div className="container-md">
            <h1 className="display-3 mb-3">Welcome back, {username}!</h1>
            <p className="lead">{welcomeMessage}</p>

            <div className="alert alert-warning mt-4" role="alert">
                🚧 This section is under development.
            </div>

            <hr className="my-4" />

            <section className="mb-4">
                <h5><i className="fa fa-star me-2" />Current Level</h5>
                <p className="mb-1"><LevelTitle level={level} /></p>
                <p>
                    <i className="fa fa-diamond me-2" />
                    EXP: <strong>{xp}</strong> / {xpToNext}
                </p>
                <small className="text-muted">Earn more EXP by:</small>
                <ul className="mt-2">
                    {expActions.map((a, i) => (
                        <li key={i}>{a.label}: <strong>{a.value}</strong></li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-coins me-2" />LensCoins</h5>
                <p>{coins} coins available</p>
                <small className="text-muted">Use LensCoins to interact with Lens:</small>
                <ul className="mt-2">
                    {coinActions.map((a, i) => (
                        <li key={i}>{a.label}: <strong>{a.value} coins</strong></li>
                    ))}
                </ul>
            </section>
        </div>
    );
}

export default Profile;
