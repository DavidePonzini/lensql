import useAuth from '../../hooks/useAuth';
import LevelTitle from './LevelTitle';
import { Coins, Experience } from '../../constants/Gamification';

function Profile() {
    const expActions = [
        {
            label: 'Solving exercises',
            value: `+${Experience.EXERCISE_SOLVED} XP`,
            className: 'text-success'
        },
        {
            label: 'Running queries',
            value: `+${Experience.QUERY_RUN} XP each`,
            className: 'text-success'
        },
        {
            label: 'Trying new, unique queries',
            value: `+${Experience.QUERY_RUN_UNIQUE} XP each`,
            className: 'text-success'
        },
        {
            label: 'Interacting with Lens',
            value: `+${Experience.ASK_HELP} XP`,
            className: 'text-success'
        }
    ];

    const coinActions = [
        {
            label: 'Ask Lens for help',
            value: `from ${Math.max(...Object.values(Coins).filter(v => v < 0))} to ${Math.min(...Object.values(Coins).filter(v => v < 0))} coins`,
            className: 'text-danger'
        },
        {
            label: 'Give feedback on Lens’ help',
            value: `+${Coins.HELP_FEEDBACK} coins`,
            className: 'text-success'
        },
    ];

    const { userInfo } = useAuth();

    const username = userInfo?.username || 'user';
    const xp = userInfo?.xp || 0;
    const xpToNext = userInfo?.xpToNextLevel || 0;
    const coins = userInfo?.coins || 0;
    const level = userInfo?.level || 0;

    return (
        <div className="container-md">
            <h1 className="display-3 mb-3">Welcome back, {username}!</h1>
            <p className="lead">Here's a look at your progress</p>

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
                        <li key={i}>{a.label}: <strong className={a.className}>{a.value}</strong></li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-coins me-2" />LensCoins</h5>
                <p>{coins} coins available</p>
                <small className="text-muted">Use LensCoins to interact with Lens:</small>
                <ul className="mt-2">
                    {coinActions.map((a, i) => (
                        <li key={i}>{a.label}: <strong className={a.className}>{a.value} coins</strong></li>
                    ))}
                </ul>
            </section>
        </div>
    );
}

export default Profile;
