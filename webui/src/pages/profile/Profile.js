import useUserInfo from '../../hooks/useUserInfo';
import LevelTitle from './LevelTitle';
import { expActions, coinActions } from '../../constants/Gamification';
import AlertUnderDevelopment from '../../components/AlertUnderDevelopment';

function Profile() {

    const { userInfo } = useUserInfo();

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
                <small className="text-muted">Earn more EXP by learning SQL:</small>
                <ul className="mt-2">
                    {expActions.map((a, i) => (
                        <li key={i}>{a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong></li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-coins me-2" />LensCoins</h5>
                <p>{coins} coins available</p>
                <small className="text-muted">Use LensCoins to interact with Lens:</small>
                <ul className="mt-2">
                    {coinActions.map((a, i) => (
                        <li key={i}>{a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong></li>
                    ))}
                </ul>
            </section>

            <hr className="my-4" />

            <section>
                <h5><i className="fa fa-trophy me-2" />Achievements</h5>
                <p>You've earned the following achievements:</p>

                <AlertUnderDevelopment />
            </section>
        </div>
    );
}

export default Profile;
