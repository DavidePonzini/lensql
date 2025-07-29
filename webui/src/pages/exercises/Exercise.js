import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import Query from './Query';

function Exercise() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { exerciseId } = useParams();

    const [exercise, setExercise] = useState(null);

    useEffect(() => {
        async function fetchAssignment() {
            const data = await apiRequest(`/api/exercises/get/${exerciseId}`, 'GET');

            setExercise(data.data);
        }

        fetchAssignment();
    }, [exerciseId, apiRequest]);

    if (!exercise) return (
        <div>{t('pages.exercises.exercise.loading')}</div>
    );

    return (
        <div className="container-md">
            <Query
                exerciseId={exerciseId}
                classId={exercise.class_id}
                exerciseText={exercise.request}
                attempts={exercise.attempts}
                hasSolution={!!exercise.solution}
            />
        </div>
    );
}

export default Exercise;
