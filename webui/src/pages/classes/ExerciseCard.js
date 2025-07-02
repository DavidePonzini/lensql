import { useState } from 'react';
import useAuth from '../../hooks/useAuth';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import SetLearningObjectives from './SetLearningObjectives';
import ExerciseUpdate from './ExerciseUpdate';

function ExerciseCard({
    children,
    title,
    exerciseId,
    isGenerated = false,
    isSubmitted,
    isTeacher = false,
    onSubmit = null,
    onUnsubmit = null,
    refreshExercises,
    learningObjectives = []
}) {
    const { apiRequest } = useAuth();

    const [submitted, setSubmitted] = useState(isSubmitted);

    async function handleSubmit() {
        await apiRequest('/api/assignments/submit', 'POST', {
            'exercise_id': exerciseId,
        });

        setSubmitted(true);
        if (onSubmit)
            onSubmit(exerciseId);
    }

    async function handleUnsubmit() {
        await apiRequest('/api/assignments/unsubmit', 'POST', {
            'exercise_id': exerciseId,
        });

        setSubmitted(false);

        if (onUnsubmit)
            onUnsubmit(exerciseId);
    }

    async function handleDelete() {
        if (!window.confirm('Are you sure you want to delete this exercise? This action cannot be undone.')) {
            return;
        }

        await apiRequest('/api/exercises/', 'DELETE', {
            'exercise_id': exerciseId,
        });

        refreshExercises();
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">{title}</h5>
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
                                            className="badge bg-secondary me-1"
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
                {!submitted && (
                    <a
                        href={`/assignments/q/${exerciseId}`}
                        className="btn btn-primary"
                    >
                        Open
                    </a>
                )}

                {submitted && onUnsubmit && (
                    <Button
                        variant="outline-danger"
                        className="ms-2"
                        onClick={handleUnsubmit}
                    >
                        Unarchive
                    </Button>
                )}
                {!submitted && onSubmit && (
                    <Button
                        variant="success"
                        className="ms-2"
                        onClick={handleSubmit}
                    >
                        Archive
                    </Button>
                )}
                {isTeacher && (
                    <>
                        <ExerciseUpdate exerciseId={exerciseId} refreshExercises={refreshExercises} />
                        <SetLearningObjectives exerciseId={exerciseId} refreshExercises={refreshExercises} />

                        <Button
                            variant="danger"
                            className="ms-2"
                            onClick={handleDelete}
                        >
                            <i className="fa fa-trash"></i> Delete
                        </Button>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ExerciseCard;