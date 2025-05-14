import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

import Query from '../components/Query';

function Assignment() {
    const { apiRequest } = useAuth();
    const { assignmentId } = useParams();
    const [assignment, setAssignment] = useState(null);

    useEffect(() => {
        async function fetchAssignment() {
            const data = await apiRequest(`/api/get-exercise?id=${assignmentId}`, 'GET');

            setAssignment(data.data);
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
