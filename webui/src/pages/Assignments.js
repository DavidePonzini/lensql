import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';

import '../styles/Assignments.css';

import AssignmentCard from '../components/AssignmentCard';

function Assignments() {
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
            const response = await apiRequest('/api/get-assignments', 'GET');

            const submitted = response.data.filter((assignment) => { return assignment.submission_ts });
            const unsubmitted = response.data.filter((assignment) => { return !assignment.submission_ts });
            setUnsubmittedAssignments(unsubmitted);
            setSubmittedAssignments(submitted);
        }

        getAssignments();
    }, [sessionStorage.getItem('username')]);       // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <>
            <h1>Incomplete</h1>
            <div className="assignments assignments-incomplete">
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
            </div>

            <h1 className="mt-2">Completed</h1>
            <div className="assignments assignments-complete">
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
            </div>
        </>
    );
}

export default Assignments;