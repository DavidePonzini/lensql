import { useState, useEffect } from 'react';
import useToken from '../hooks/useToken';

import AssignmentCard from '../components/AssignmentCard';

function Assignments() {
    const [assignments, setAssignments] = useState([]);
    const [token] = useToken();

    useEffect(() => {
        async function getAssignments() {
            try {
                const response = await fetch(`/api/get-assignments`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'authorization': `Bearer ${token}`,
                    }
                });

                const data = await response.json();
                setAssignments(data.data);
            } catch (error) {
                alert('Error fetching assignments:' + error);
                console.error(error);
                return [];
            }
        }

        getAssignments();
    }, [token]);

    return (
        <>
            <h1>Assignments</h1>
            <div>
                {assignments.map((assignment) => {
                    return (
                        <AssignmentCard
                            assignmentId={assignment.id}
                            isGenerated={assignment.is_ai_generated}
                            key={assignment.id}
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