import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import CardList from '../../components/CardList';

import ExerciseCard from './ExerciseCard';
import ExerciseAdd from './ExerciseAdd';

function ExerciseList() {
    const { datasetId } = useParams();
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [isOwner, setIsOwner] = useState(false);
    const [exercises, setExercises] = useState([]);
    const [loading, setLoading] = useState(true);

    const getExercises = useCallback(async () => {
        setLoading(true);
        const response = await apiRequest(`/api/exercises?dataset_id=${datasetId}`, 'GET');

        const sortedExercises = (response.data ?? []).slice().sort((a, b) => {
            return a.title.localeCompare(b.title, undefined, { numeric: true, sensitivity: 'base' });
        });


        setExercises(sortedExercises);
        setLoading(false);
    }, [datasetId, apiRequest]);

    useEffect(() => {
        getExercises();
    }, [getExercises]);

    useEffect(() => {
        async function checkIfOwner() {
            const response = await apiRequest(`/api/datasets/is-owner/${datasetId}`, 'GET');
            setIsOwner(response.is_owner);
        }

        checkIfOwner();
    }, [datasetId, apiRequest]);

    return (
        <div className="container-md">
            <h1>{t('pages.datasets.exercise_list.title')}</h1>

            {isOwner && (
                <div className="mt-4">
                    <ExerciseAdd
                        refresh={getExercises}
                        datasetId={datasetId}
                    />

                    <hr />
                </div>
            )}

            <CardList>
                {exercises.length === 0 && !loading && (
                    <p className="no-assignments">{t('pages.datasets.exercise_list.none')}</p>
                )}

                {loading && (
                    <p className="loading">{t('pages.datasets.exercise_list.loading')}</p>
                )}

                {exercises.map((exercise) => (
                    <ExerciseCard
                        key={exercise.exercise_id}
                        exerciseId={exercise.exercise_id}
                        isGenerated={exercise.is_ai_generated}
                        isSolved={exercise.is_solved}
                        isHidden={exercise.is_hidden}
                        isOwner={isOwner}
                        hasSolution={exercise.has_solution}
                        title={exercise.title}
                        refresh={getExercises}
                        learningObjectives={exercise.learning_objectives}
                    >
                        {exercise.request}
                    </ExerciseCard>
                ))}
            </CardList>
        </div>
    );
}

export default ExerciseList;
