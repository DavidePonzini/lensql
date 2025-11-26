import { useTranslation } from 'react-i18next';

import useUserInfo from '../../hooks/useUserInfo';
import useGamificationData from '../../hooks/useGamificationData';

import LevelTitle from './LevelTitle';

import AlertUnderDevelopment from '../../components/AlertUnderDevelopment';
import ChangePasswordButton from './ChangePasswordButton';

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
            <h1 className="display-3 mb-3">{t('pages.profile.profile.welcome', { username })}</h1>

            <hr className="my-4" />

            <p className="lead">{t('pages.profile.profile.settings')}</p>
            <div className="mb-3">
                <ChangePasswordButton />
            </div>

            <hr className="my-4" />

            <p className="lead">{t('pages.profile.profile.progress')}</p>
            <section className="mb-4">
                <h5><i className="fa fa-star me-2" />{t('pages.profile.profile.level.title')}</h5>
                <p className="mb-1"><LevelTitle level={level} /></p>
                <p>
                    <i className="fa fa-diamond me-2" />
                    {t('pages.profile.profile.level.exp', { xp, xpToNext })}
                </p>
                <small className="text-muted">{t('pages.profile.profile.level.tip')}</small>
                <ul className="mt-2">
                    {expActions.map((a, i) => (
                        <li key={i}>
                            {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                        </li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-coins me-2" />{t('pages.profile.profile.coins.title')}</h5>
                <p>{t('pages.profile.profile.coins.available', { coins })}</p>
                <small className="text-muted">{t('pages.profile.profile.coins.tip')}</small>
                <ul className="mt-2">
                    {coinActions.map((a, i) => (
                        <li key={i}>
                            {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                        </li>
                    ))}
                </ul>
            </section>

            <section>
                <h5><i className="fa fa-trophy me-2" />{t('pages.profile.profile.achievements.title')}</h5>
                <p>{t('pages.profile.profile.achievements.text')}</p>
                <AlertUnderDevelopment />
            </section>
        </div>
    );
}

export default Profile;
