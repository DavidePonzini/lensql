import '../styles/AssignmentCard.css';

import { useState } from 'react';
import useAuth from '../hooks/useAuth';

function AssignmentCard({ children, assignmentTitle, assignmentId, isGenerated = false, deadlineDate, submssionDate = null, onSubmit, onUnsubmit }) {
    const { apiRequest } = useAuth();

    const [isSubmitted, setIsSubmitted] = useState(submssionDate !== null);
    const remainingTime = deadlineDate ? new Date(deadlineDate) - new Date() : null;


    async function handleSubmit() {
        const response = await apiRequest('/api/submit-assignment', 'POST', {
            'exercise_id': assignmentId,
        });

        setIsSubmitted(true);
        onSubmit(assignmentId);
    }

    async function handleUnsubmit() {
        const response = await apiRequest('/api/unsubmit-assignment', 'POST', {
            'exercise_id': assignmentId,
        });

        setIsSubmitted(false);
        onUnsubmit(assignmentId);
    }

    return (
        <div className="card" >
            <div className="card-body">
                <h5 className="card-title">{assignmentTitle}</h5>
                <p className="card-text">{children}</p>

                {!isSubmitted && (
                    <a
                        href={`/assignments/${assignmentId}`}
                        className="btn btn-primary"
                    >
                        View Assignment
                    </a>
                )}

                {isSubmitted ? (
                    <button
                        className="ms-2 btn btn-danger"
                        onClick={handleUnsubmit}
                    >
                        Unsubmit
                    </button>
                ) : (
                    <button
                        className="ms-2 btn btn-success"
                        onClick={handleSubmit}
                    >
                        Submit
                    </button>
                )}
            </div>
        </div>
    );
}

export default AssignmentCard;