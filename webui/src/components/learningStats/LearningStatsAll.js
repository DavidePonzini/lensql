import { useTranslation } from 'react-i18next';
import LearningStatsQueries from "./LearningStatsQueries";
import LearningStatsMessages from "./LearningStatsMessages";
import LearningStatsErrors from "./LearningStatsErrors";

function LearningStatsAll({ classId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();

    return (
        <>
            <h2 id="queries">
                {isTeacher ? t('components.learningStats.learning.queries_teacher') : t('components.learningStats.learning.queries_student')}
            </h2>
            <LearningStatsQueries classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="messages">{t('components.learningStats.learning.messages')}</h2>
            <LearningStatsMessages classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="errors">{t('components.learningStats.learning.errors')}</h2>
            <LearningStatsErrors classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />
        </>
    );
}

export default LearningStatsAll;
