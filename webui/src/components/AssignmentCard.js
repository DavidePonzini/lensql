import '../styles/AssignmentCard.css';

import { useState } from 'react';
import useAuth from '../hooks/useAuth';

function AssignmentCard({ children, assignmentTitle, assignmentId, isGenerated = false, deadlineDate, isSubmitted, onSubmit, onUnsubmit }) {
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
        <div className="card" >
            <div className="card-body">
                <h5 className="card-title">{assignmentTitle}</h5>
                <p className="card-text">{children}</p>


                {!submitted && (
                    <a
                        href={`/assignments/q/${assignmentId}`}
                        className="btn btn-primary"
                    >
                        View Assignment
                    </a>
                )}

                {submitted && onUnsubmit && (
                    <button
                        className="ms-2 btn btn-danger"
                        onClick={handleUnsubmit}
                    >
                        Unarchive
                    </button>
                )}
                {!submitted && onSubmit && (
                    <button
                        className="ms-2 btn btn-success"
                        onClick={handleSubmit}
                    >
                        Archive
                    </button>
                )}
            </div>
        </div>
    );
}

export default AssignmentCard;