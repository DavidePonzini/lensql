import { useState, useEffect } from 'react';
import useAuth from '../../hooks/useAuth';

import AssignmentCard from './AssignmentCard';

function CardList({ children }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
        }}>
            {children}
        </div>
    );
}

function AssignmentList() {
    const { apiRequest } = useAuth();

    const [unsubmittedAssignments, setUnsubmittedAssignments] = useState([]);
    const [submittedAssignments, setSubmittedAssignments] = useState([]);

    function handleSubmit(assignmentId) {
        const assignment = unsubmittedAssignments.find((assignment) => assignment.id === assignmentId);
        if (assignment) {
            setUnsubmittedAssignments((prevAssignments) => prevAssignments.filter((assignment) => assignment.id !== assignmentId));
            setSubmittedAssignments((prevAssignments) => [...prevAssignments, assignment]);
        }
    }

    function handleUnsubmit(assignmentId) {
        const assignment = submittedAssignments.find((assignment) => assignment.id === assignmentId);
        if (assignment) {
            setSubmittedAssignments((prevAssignments) => prevAssignments.filter((assignment) => assignment.id !== assignmentId));
            setUnsubmittedAssignments((prevAssignments) => [...prevAssignments, assignment]);
        }
    }

    useEffect(() => {
        async function getAssignments() {
            const response = await apiRequest('/api/assignments/list', 'GET');

            const submitted = response.data.filter((assignment) => { return assignment.submission_ts });
            const unsubmitted = response.data.filter((assignment) => { return !assignment.submission_ts });
            setUnsubmittedAssignments(unsubmitted);
            setSubmittedAssignments(submitted);
        }

        getAssignments();
    }, [sessionStorage.getItem('username')]);       // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <>
            <h1>Assignments</h1>
            <CardList>
                {unsubmittedAssignments.length === 0 && <p className="no-assignments">No assignments</p>}

                {unsubmittedAssignments.map((assignment) => {
                    return (
                        <AssignmentCard
                            assignmentId={assignment.id}
                            isGenerated={assignment.is_ai_generated}
                            key={assignment.id}
                            deadlineDate={assignment.deadline_ts}
                            isSubmitted={false}
                            assignmentTitle={assignment.title}
                            onSubmit={handleSubmit}
                            onUnsubmit={handleUnsubmit}
                        >
                            {assignment.request}
                        </AssignmentCard>
                    );
                })}
            </CardList>

            <h1 className="mt-3">Archived</h1>
            <CardList>
                {submittedAssignments.length === 0 && <p className="no-assignments">No archived assignments</p>}

                {submittedAssignments.map((assignment) => {
                    return (
                        <AssignmentCard
                            assignmentId={assignment.id}
                            isGenerated={assignment.is_ai_generated}
                            key={assignment.id}
                            deadlineDate={assignment.deadline_ts}
                            isSubmitted={true}
                            assignmentTitle={assignment.title}
                            onSubmit={handleSubmit}
                            onUnsubmit={handleUnsubmit}
                        >
                            {assignment.request}
                        </AssignmentCard>
                    );
                })}
            </CardList>
        </>
    );
}

export default AssignmentList;