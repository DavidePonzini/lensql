import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';

import Query from './Query';

function Assignment() {
    const { apiRequest } = useAuth();
    const { assignmentId } = useParams();
    const [assignment, setAssignment] = useState(null);
    
    useEffect(() => {
        async function fetchAssignment() {
            const data = await apiRequest(`/api/exercises?id=${assignmentId}`, 'GET');

            setAssignment(data.data);
        }

        fetchAssignment();
    }, [assignmentId]);     // eslint-disable-line react-hooks/exhaustive-deps

    if (!assignment) return (
        <div>Loading...</div>
    );

    return (
        <Query
            exerciseId={assignmentId}
            exerciseText={assignment.request}
            datasetId={assignment.dataset_id}
        />
    );
}

export default Assignment;
