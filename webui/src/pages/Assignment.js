import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import useToken from '../hooks/useToken';

import Query from '../components/Query';

function Assignment() {
    const [token] = useToken();
    const { assignmentId } = useParams();
    const [assignment, setAssignment] = useState(null);

    useEffect(() => {
        async function fetchAssignment() {
            try {
                const response = await fetch(`/api/get-exercise?id=${assignmentId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'authorization': `Bearer ${token}`,
                    },
                });
                const data = await response.json();
                setAssignment(data.data);
            }
            catch (error) {
                alert('Error fetching assignment:', error);
                console.error(error);
                return;
            }
        }

        fetchAssignment();
    }, [assignmentId]);

    if (!assignment) return (
        <div>Loading...</div>
    );

    return (
        <Query
            exerciseId={assignmentId}
            exerciseText={assignment.request}
        />
    );
}

export default Assignment;
