import useUserInfo from '../../hooks/useUserInfo';
import LevelTitle from './LevelTitle';
import useGamificationData from '../../hooks/useGamificationData';
import AlertUnderDevelopment from '../../components/AlertUnderDevelopment';
import { useTranslation } from 'react-i18next';

function Profile() {
    const { userInfo } = useUserInfo();
    const { expActions, coinActions } = useGamificationData();
    const { t } = useTranslation();

    const username = userInfo?.username || 'user';
    const xp = userInfo?.xp || 0;
    const xpToNext = userInfo?.xpToNextLevel || 0;
    const coins = userInfo?.coins || 0;
    const level = userInfo?.level || 0;

    return (
        <div className="container-md">
            <h1 className="display-3 mb-3">{t('profile.home.welcome', { username })}</h1>
            <p className="lead">{t('profile.home.progress')}</p>

            <hr className="my-4" />

            <section className="mb-4">
                <h5><i className="fa fa-star me-2" />{t('profile.home.level.title')}</h5>
                <p className="mb-1"><LevelTitle level={level} /></p>
                <p>
                    <i className="fa fa-diamond me-2" />
                    {t('profile.home.level.exp', { xp, xpToNext })}
                </p>
                <small className="text-muted">{t('profile.home.level.tip')}</small>
                <ul className="mt-2">
                    {expActions.map((a, i) => (
                        <li key={i}>
                            {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                        </li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-coins me-2" />{t('profile.home.coins.title')}</h5>
                <p>{t('profile.home.coins.available', { coins })}</p>
                <small className="text-muted">{t('profile.home.coins.tip')}</small>
                <ul className="mt-2">
                    {coinActions.map((a, i) => (
                        <li key={i}>
                            {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                        </li>
                    ))}
                </ul>
            </section>

            <hr className="my-4" />

            <section>
                <h5><i className="fa fa-trophy me-2" />{t('profile.home.achievements.title')}</h5>
                <p>{t('profile.home.achievements.text')}</p>
                <AlertUnderDevelopment />
            </section>
        </div>
    );
}

export default Profile;
