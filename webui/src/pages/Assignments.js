import { useState, useEffect } from 'react';

import AssignmentCard from '../components/AssignmentCard';

function Assignments() {
    const [assignments, setAssignments] = useState([]);


    async function getAssignments() {
        const username = sessionStorage.getItem('username');

        try {
            const response = await fetch(`/api/get-assignments?username=${username}`);

            const data = await response.json();
            console.log(data);
            setAssignments(data.data);
        } catch (error) {
            alert('Error fetching assignments:', error);
            console.error(error);
            return [];
        }
    }

    useEffect(getAssignments, []);

    return (
        <>
            <h1>Assignments</h1>
            <div>
                {assignments.map((assignment) => {
                    return (
                        <AssignmentCard
                            assignmentId={assignment.id}
                            isGenerated={assignment.is_ai_generated}

                        >
                            {assignment.request}
                        </AssignmentCard>
                    );
                })
                }
            </div>
        </>
    );
}

export default Assignments;