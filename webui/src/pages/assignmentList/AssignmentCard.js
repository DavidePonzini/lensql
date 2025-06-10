import { useState } from 'react';
import useAuth from '../../hooks/useAuth';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

function AssignmentCard({
    children,
    assignmentTitle,
    assignmentId,
    isGenerated = false,
    isSubmitted,
    onSubmit,
    onUnsubmit,
    learningObjectives = []
}) {
    const { apiRequest } = useAuth();

    const [submitted, setSubmitted] = useState(isSubmitted);

    async function handleSubmit() {
        await apiRequest('/api/assignments/submit', 'POST', {
            'exercise_id': assignmentId,
        });

        setSubmitted(true);
        onSubmit(assignmentId);
    }

    async function handleUnsubmit() {
        await apiRequest('/api/assignments/unsubmit', 'POST', {
            'exercise_id': assignmentId,
        });

        setSubmitted(false);
        onUnsubmit(assignmentId);
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">{assignmentTitle}</h5>
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

                    </div>
                </div>

                {isGenerated && (
                    <span className="badge bg-info mx-1 my-2">
                        AI Generated
                    </span>
                )}
            </Card.Body>

            <Card.Footer>
                {!submitted && (
                    <a
                        href={`/assignments/q/${assignmentId}`}
                        className="btn btn-primary"
                    >
                        View Assignment
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
            </Card.Footer>
        </Card>
    );
}

export default AssignmentCard;