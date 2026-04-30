import { useTranslation } from 'react-i18next';
import Card from 'react-bootstrap/Card';

import LearningStatsQueries from "./LearningStatsQueries";
import LearningStatsMessages from "./LearningStatsMessages";
import LearningStatsErrors from "./LearningStatsErrors";
import "./LearningStats.css";

function LearningStatsAll({ datasetId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();

    return (
        <div className="learning-stats-page">
            <Card className="learning-stats-section learning-stats-section--queries">
                <Card.Body className="learning-stats-section__body">
                    <div className="learning-stats-section__header">
                        <span className="learning-stats-section__eyebrow" id="queries">
                            01
                        </span>
                        <h2 className="learning-stats-section__title">
                            {isTeacher ? t('components.learningStats.learning.queries_teacher') : t('components.learningStats.learning.queries_student')}
                        </h2>
                    </div>
                    <LearningStatsQueries datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />
                </Card.Body>
            </Card>

            <Card className="learning-stats-section learning-stats-section--errors">
                <Card.Body className="learning-stats-section__body">
                    <div className="learning-stats-section__header">
                        <span className="learning-stats-section__eyebrow" id="errors">
                            02
                        </span>
                        <h2 className="learning-stats-section__title">{t('components.learningStats.learning.errors')}</h2>
                    </div>
                    <LearningStatsErrors datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />
                </Card.Body>
            </Card>

            <Card className="learning-stats-section learning-stats-section--messages">
                <Card.Body className="learning-stats-section__body">
                    <div className="learning-stats-section__header">
                        <span className="learning-stats-section__eyebrow" id="messages">
                            03
                        </span>
                        <h2 className="learning-stats-section__title">{t('components.learningStats.learning.messages')}</h2>
                    </div>
                    <LearningStatsMessages datasetId={datasetId} exerciseId={exerciseId} isTeacher={isTeacher} />
                </Card.Body>
            </Card>
        </div>
    );
}

export default LearningStatsAll;
