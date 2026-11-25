import { useTranslation } from "react-i18next";
import { Navigate, useNavigate, useParams } from 'react-router-dom';

import useUserInfo from "../../hooks/useUserInfo";

import LearningStatsAll from "../../components/learningStats/LearningStatsAll";

function Learning() {
    const { userInfo } = useUserInfo();
    const { t } = useTranslation();
    const { tab } = useParams();
    const navigate = useNavigate();

    if (!['execution', 'errors', 'assistance'].includes(tab)) {
        return <Navigate to="/learning/execution" replace />;
    }

    return (
        <div className="container-md">
            <h1 className="display-3">
                {t('pages.profile.learning.title', { username: userInfo?.username || 'user' })}
            </h1>
            <p className="lead">{t('pages.profile.learning.subtitle')}</p>

            <hr />
            <LearningStatsAll requestedTab={tab} onTabChange={id => navigate(`/learning/${id}`)} />
        </div>
    );
}

export default Learning;
