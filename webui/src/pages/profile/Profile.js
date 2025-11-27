import { useTranslation } from 'react-i18next';

import useUserInfo from '../../hooks/useUserInfo';
import useGamificationData from '../../hooks/useGamificationData';

import LevelTitle from './LevelTitle';

import AlertUnderDevelopment from '../../components/AlertUnderDevelopment';
import ChangePassword from './ChangePassword';

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

            <h2>{t('pages.profile.profile.settings')}</h2>
            <div className="mb-3">
                <a className='btn btn-primary' href='#change-password' role='button' data-bs-toggle='collapse' aria-expanded='false' aria-controls='change-password'>
                    {t('pages.profile.profile.change_password.title')}
                </a>

                <div id="change-password" className="collapse mt-3" style={{maxWidth: 500}}>
                    <ChangePassword />
                </div>
            </div>

            <hr className="my-4" />

            <h2>{t('pages.profile.profile.progress')}</h2>
            {/*
                TODO: make this part visually similar to learning stats
            
                |----------------------------------------------------------|
                |           |               | How to earn more EXP         | 
                |   LEVEL   | EXP Pie Chart | - ...                        |
                |     5     |               | - ...                        | 
                |----------------------------------------------------------|
                |   <i>     | How to earn more Coins                       | 
                |  Coins    | - ...                                        | 
                |   7       | - ...                                        | 
                |----------------------------------------------------------|
                | Achievements                                             |
                | X | X | X                                                |
                | X | X | X                                                |
                | X | X | X                                                |
                |----------------------------------------------------------|
            */}
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
