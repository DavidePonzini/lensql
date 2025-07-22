import { useState } from 'react';
import useAuth from '../../hooks/useAuth';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import ButtonModal from '../../components/ButtonModal';
import SetLearningObjectives from './SetLearningObjectives';
import ExerciseUpdate from './ExerciseUpdate';
import { NavLink } from 'react-router-dom';
import LearningStatsAll from '../../components/LearningStatsAll';

function ExerciseCard({
    children,
    title,
    exerciseId,
    isGenerated = false,
    isSubmitted,
    isTeacher = false,
    isHidden = false,
    onSubmit = null,
    onUnsubmit = null,
    refresh,
    learningObjectives = []
}) {
    const { apiRequest } = useAuth();

    const [submitted, setSubmitted] = useState(isSubmitted);
    const [hidden, setHidden] = useState(isHidden);

    async function handleSubmit() {
        await apiRequest('/api/exercises/submit', 'POST', {
            'exercise_id': exerciseId,
            'value': true,
        });

        setSubmitted(true);
        if (onSubmit)
            onSubmit(exerciseId);
    }

    async function handleUnsubmit() {
        await apiRequest('/api/exercises/submit', 'POST', {
            'exercise_id': exerciseId,
            'value': false,
        });

        setSubmitted(false);
        if (onUnsubmit)
            onUnsubmit(exerciseId);
    }

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
        if (!window.confirm('Are you sure you want to delete this exercise? This action cannot be undone.')) {
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
                    {hidden && (
                        <span className="badge bg-secondary ms-2">
                            Hidden
                        </span>
                    )}
                </h5>
            </Card.Header>

            <Card.Body>
                <Card.Text>
                    {children}
                </Card.Text>

                <div className='row my-2'>
                    {learningObjectives.length > 0 && (
                        <>
                            <div className='col'>
                                <b>Learning Objectives:</b>
                                <div>
                                    {learningObjectives.map(({ objective, description }, index) => (
                                        <span
                                            key={index}
                                            className="badge bg-secondary me-2"
                                            data-bs-toggle="tooltip"
                                            data-bs-placement="bottom"
                                            data-bs-title={description}
                                            style={{
                                                cursor: 'default',
                                            }}
                                        >
                                            {objective}
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
                                AI Generated
                            </span>
                        )}
                    </div>
                </div>
            </Card.Body>

            <Card.Footer>
                {submitted ? (
                    <Button
                        variant="outline-danger"
                        className="me-2 mb-1"
                        onClick={handleUnsubmit}
                    >
                        Unarchive
                    </Button>
                ) : (
                    <>
                        <NavLink
                            to={`/exercises/${exerciseId}`}
                            className="btn btn-primary me-2 mb-1"
                        >
                            Open
                        </NavLink>

                        <Button
                            variant="outline-success"
                            className="me-2 mb-1"
                            onClick={handleSubmit}
                        >
                            Archive
                        </Button>

                        {isTeacher && (
                            <>
                                <div className='vr me-2 mb-1' style={{
                                    verticalAlign: 'middle',
                                    height: '2.5rem',
                                }} />

                                <ButtonModal
                                    className="btn btn-info me-2 mb-1"
                                    title="Learning Analytics"
                                    fullscreen={true}
                                    buttonText="Learning Analytics"
                                >
                                    <LearningStatsAll exerciseId={exerciseId} />
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
                                        <i className="fa fa-eye"></i> Make Visible
                                    </Button>
                                ) : (
                                    <Button
                                        variant="outline-secondary"
                                        className="me-2 mb-1"
                                        onClick={handleHide}
                                    >
                                        <i className="fa fa-eye-slash"></i> Hide
                                    </Button>
                                )}

                                <Button
                                    variant="danger"
                                    className="me-2 mb-1"
                                    onClick={handleDelete}
                                >
                                    <i className="fa fa-trash"></i> Delete
                                </Button>
                            </>
                        )}
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ExerciseCard;