import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';
import useGamificationData from '../../hooks/useGamificationData';

import LevelTitle from './LevelTitle';

import ChangePassword from './ChangePassword';
import Badges from './Badges';

function Profile() {
    const { apiRequest } = useAuth();
    const { userInfo, setTeacherStatus } = useUserInfo();
    const { expActions, coinActions } = useGamificationData();
    const { t } = useTranslation();

    const username = userInfo?.username || 'user';
    const xp = userInfo?.xp || 0;
    const xpToNext = userInfo?.xpToNextLevel || 0;
    const coins = userInfo?.coins || 0;
    const level = userInfo?.level || 0;
    const isTeacher = userInfo?.isTeacher || false;

    async function toggleTeacherMode() {
        const newValue = !isTeacher;
        const response = await apiRequest('/api/users/set-teacher', 'POST', {
            is_teacher: newValue,
        });

        if (response.success) {
            setTeacherStatus(newValue);
        }
    }

    return (
        <div className="container-md">
            <h1 className="display-3 mb-3">{t('pages.profile.profile.welcome', { username })}</h1>

            <hr className="my-4" />

            <h2>{t('pages.profile.profile.settings')}</h2>
            <div className="mb-3">
                <div className="row mb-2">
                    <div className="col-sm-3">
                        <button className='btn btn-primary' type='button' data-bs-toggle='collapse' data-bs-target='#change-password' aria-expanded='false' aria-controls='change-password'>
                            {t('pages.profile.profile.change_password.title')}
                        </button>

                        <button className={`btn ${isTeacher ? 'btn-outline-secondary' : 'btn-outline-primary'} mt-2`} onClick={toggleTeacherMode}>
                            {isTeacher ? t('pages.profile.profile.teacher_mode.disable') : t('pages.profile.profile.teacher_mode.enable')}
                        </button>

                        <a href="mailto:davide.ponzini@edu.unige.it?subject=[LENSQL] Support Request" className="btn btn-warning mt-2">
                            {t('pages.profile.profile.contact_support')}
                        </a>
                    </div>
                    <div className="col-sm-9">
                        <div id="change-password" className="collapse">
                            <ChangePassword />
                        </div>
                    </div>
                </div>
            </div>

            <hr className="my-4" />

            <h2>{t('pages.profile.profile.progress')}</h2>
            <section className="mb-4">
                <div className='row'>
                    <div className='col-md-6'>
                        <h5><i className="fa fa-star me-2" />{t('pages.profile.profile.level.title')}</h5>
                        <p className="mb-1"><LevelTitle level={level} /></p>
                        <p>
                            <i className="fa fa-diamond me-2" />
                            {t('pages.profile.profile.level.exp', { xp, xpToNext })}
                        </p>

                        <button className="btn btn-sm btn-outline-secondary mb-2" type='button' data-bs-toggle='collapse' data-bs-target='#exp-actions' aria-expanded='false' aria-controls='exp-actions'>
                            {t('pages.profile.profile.level.earn_exp')}
                        </button>

                        <div id="exp-actions" className="collapse">
                            <small className="text-muted">{t('pages.profile.profile.level.tip')}</small>
                            <ul className="mt-2">
                                {expActions.map((a, i) => (
                                    <li key={i}>
                                        {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className='col-md-6'>
                        <h5><i className="fa fa-coins me-2" />{t('pages.profile.profile.coins.title')}</h5>
                        <p>{t('pages.profile.profile.coins.available', { coins })}</p>

                        <button className="btn btn-sm btn-outline-secondary mb-2" type='button' data-bs-toggle='collapse' data-bs-target='#coin-actions' aria-expanded='false' aria-controls='coin-actions'>
                            {t('pages.profile.profile.coins.earn_coins')}
                        </button>

                        <div id="coin-actions" className="collapse">
                            <small className="text-muted">{t('pages.profile.profile.coins.tip')}</small>
                            <ul className="mt-2">
                                {coinActions.map((a, i) => (
                                    <li key={i}>
                                        {a.label}: <strong className={a.positive ? 'text-success' : 'text-danger'}>{a.value}</strong>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <section>
                <h5><i className="fa fa-trophy me-2" />{t('pages.profile.profile.achievements.title')}</h5>
                <p>{t('pages.profile.profile.achievements.text')}</p>
                <Badges />
            </section>
        </div >
    );
}

export default Profile;
