import { useTranslation } from 'react-i18next';

import LearningStatsQueries from "./LearningStatsQueries";
import LearningStatsMessages from "./LearningStatsMessages";
import LearningStatsErrors from "./LearningStatsErrors";

function LearningStatsAll({ datasetId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();

    return (
        <>
            <h2 id="queries">
                {isTeacher ? t('components.learningStats.learning.queries_teacher') : t('components.learningStats.learning.queries_student')}
            </h2>
            <LearningStatsQueries datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="errors">{t('components.learningStats.learning.errors')}</h2>
            <LearningStatsErrors datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="messages">{t('components.learningStats.learning.messages')}</h2>
            <LearningStatsMessages datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />
        </>
    );
}

export default LearningStatsAll;
