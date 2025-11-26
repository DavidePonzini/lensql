import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';
import LearningStatsAll from '../../components/learningStats/LearningStatsAll';

import SetLearningObjectives from './SetLearningObjectives';
import ExerciseUpdate from './ExerciseUpdate';


function ExerciseCard({
    children,
    title,
    exerciseId,
    isGenerated = false,
    isSolved = false,
    isTeacher = false,
    isHidden = false,
    refresh,
    learningObjectives = []
}) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [hidden, setHidden] = useState(isHidden);

    async function handleHide() {
        await apiRequest('/api/exercises/hide', 'POST', {
            'exercise_id': exerciseId,
            'value': true,
        });

        setHidden(true);
    }

    async function handleUnhide() {
        await apiRequest('/api/exercises/hide', 'POST', {
            'exercise_id': exerciseId,
            'value': false,
        });

        setHidden(false);
    }

    async function handleDelete() {
        if (!window.confirm(t('pages.datasets.exercise.delete_confirm'))) {
            return;
        }

        const result = await apiRequest('/api/exercises', 'DELETE', {
            'exercise_id': exerciseId,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        refresh();
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">
                    {title}
                    {hidden && <span className="badge bg-secondary ms-2">{t('pages.datasets.exercise.hidden')}</span>}
                    {isSolved && <span className="badge bg-success ms-2">{t('pages.datasets.exercise.solved')}</span>}
                </h5>
            </Card.Header>

            <Card.Body>
                <Card.Text>{children}</Card.Text>

                <div className='row my-2'>
                    {isTeacher && learningObjectives.length > 0 && (
                        <>
                            <div className='col'>
                                <b>{t('pages.datasets.exercise.objectives')}:</b>
                                <div>
                                    {learningObjectives.map((o, index) => (
                                        <span
                                            key={index}
                                            className="badge bg-secondary me-2"
                                            data-bs-toggle="tooltip"
                                            data-bs-placement="bottom"
                                            data-bs-title={t(`learning_objectives.objectives.${o}.description`, o)}
                                            style={{ cursor: 'default' }}
                                        >
                                            {t(`learning_objectives.objectives.${o}.label`, o)}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className='col-auto d-flex'>
                                <div className='vr'></div>
                            </div>
                        </>
                    )}

                    <div className='col'>
                        {isGenerated && (
                            <span className="badge bg-info mx-1 my-2">
                                {t('pages.datasets.exercise.generated')}
                            </span>
                        )}
                    </div>
                </div>
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={`/exercises/${exerciseId}`}
                    className="btn btn-primary me-2 mb-1"
                >
                    {t('pages.datasets.exercise.open')}
                </NavLink>

                {isTeacher && (
                    <>
                        <div className='vr me-2 mb-1' style={{ verticalAlign: 'middle', height: '2.5rem' }} />

                        <ButtonModal
                            className="btn btn-info me-2 mb-1"
                            title={t('pages.datasets.exercise.student_analytics')}
                            fullscreen
                            buttonText={t('pages.datasets.exercise.student_analytics')}
                        >
                            <LearningStatsAll exerciseId={exerciseId} isTeacher={isTeacher} />
                        </ButtonModal>

                        <ExerciseUpdate
                            exerciseId={exerciseId}
                            refreshExercises={refresh}
                            className="btn btn-warning me-2 mb-1"
                        />

                        <SetLearningObjectives
                            exerciseId={exerciseId}
                            refreshExercises={refresh}
                            className="btn btn-warning me-2 mb-1"
                        />

                        {hidden ? (
                            <Button
                                variant="secondary"
                                className="me-2 mb-1"
                                onClick={handleUnhide}
                            >
                                <i className="fa fa-eye"></i> {t('pages.datasets.exercise.show')}
                            </Button>
                        ) : (
                            <Button
                                variant="outline-secondary"
                                className="me-2 mb-1"
                                onClick={handleHide}
                            >
                                <i className="fa fa-eye-slash"></i> {t('pages.datasets.exercise.hide')}
                            </Button>
                        )}

                        <Button
                            variant="danger"
                            className="me-2 mb-1"
                            onClick={handleDelete}
                        >
                            <i className="fa fa-trash"></i> {t('pages.datasets.exercise.delete')}
                        </Button>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ExerciseCard;
