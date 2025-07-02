import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';

import Query from './Query';

function Exercise() {
    const { apiRequest } = useAuth();
    const { exerciseId } = useParams();
    const [exercise, setExercise] = useState(null);

    useEffect(() => {
        async function fetchAssignment() {
            const data = await apiRequest(`/api/exercises?id=${exerciseId}`, 'GET');

            setExercise(data.data);
        }

        fetchAssignment();
    }, [exerciseId, apiRequest]);

    if (!exercise) return (
        <div>Loading...</div>
    );

    return (
        <div className="container-md">
            <Query
                exerciseId={exerciseId}
                exerciseText={exercise.request}
                datasetName={exercise.dataset_name}
            />
        </div>
    );
}

export default Exercise;
