import useUserInfo from "../../hooks/useUserInfo";
import LearningStatsAll from "../../components/LearningStatsAll";
import { useTranslation } from "react-i18next";

function Learning() {
    const { userInfo } = useUserInfo();
    const { t } = useTranslation();

    return (
        <div className="container-md">
            <h1 className="display-3">
                {t('pages.profile.learning.title', { username: userInfo?.username || 'user' })}
            </h1>
            <p className="lead">{t('pages.profile.learning.subtitle')}</p>

            <hr />
            <LearningStatsAll />
        </div>
    );
}

export default Learning;
