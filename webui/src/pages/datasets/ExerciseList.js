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

    const [isTeacher, setIsTeacher] = useState(false);
    const [exercises, setExercises] = useState([]);

    const getExercises = useCallback(async () => {
        const response = await apiRequest(`/api/exercises?dataset_id=${datasetId}`, 'GET');

        const sortedExercises = (response.data ?? []).slice().sort((a, b) => {
            return (a.exercise_id > b.exercise_id) - (a.exercise_id < b.exercise_id);
        });


        setExercises(sortedExercises);
    }, [datasetId, apiRequest]);

    useEffect(() => {
        getExercises();
    }, [getExercises]);

    useEffect(() => {
        async function checkIfTeacher() {
            const response = await apiRequest(`/api/datasets/is-teacher/${datasetId}`, 'GET');
            setIsTeacher(response.is_teacher);
        }

        checkIfTeacher();
    }, [datasetId, apiRequest]);

    return (
        <div className="container-md">
            <h1>{t('pages.datasets.exercise_list.title')}</h1>
            <CardList>
                {exercises.length === 0 && (
                    <p className="no-assignments">{t('pages.datasets.exercise_list.none')}</p>
                )}

                {exercises.map((exercise) => (
                    <ExerciseCard
                        key={exercise.exercise_id}
                        exerciseId={exercise.exercise_id}
                        isGenerated={exercise.is_ai_generated}
                        isSolved={exercise.is_solved}
                        isHidden={exercise.is_hidden}
                        isTeacher={isTeacher}
                        title={exercise.title}
                        refresh={getExercises}
                        learningObjectives={exercise.learning_objectives}
                    >
                        {exercise.request}
                    </ExerciseCard>
                ))}
            </CardList>

            {isTeacher && (
                <>
                    <hr />
                    <ExerciseAdd
                        refresh={getExercises}
                        datasetId={datasetId}
                    />
                </>
            )}
        </div>
    );
}

export default ExerciseList;
