import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import CardList from '../../components/CardList';

import ExerciseCard from './ExerciseCard';
import ExerciseAdd from './ExerciseAdd';

function ExerciseList() {
    const { classId } = useParams();
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [isTeacher, setIsTeacher] = useState(false);
    const [unsubmittedExercises, setUnsubmittedExercises] = useState([]);
    const [submittedExercises, setSubmittedExercises] = useState([]);

    function handleSubmit(exercise) {
        setUnsubmittedExercises((prev) => prev.filter((e) => e.exercise_id !== exercise.exercise_id));
        setSubmittedExercises((prev) => [...prev, exercise]);
    }

    function handleUnsubmit(exercise) {
        setSubmittedExercises((prev) => prev.filter((e) => e.exercise_id !== exercise.exercise_id));
        setUnsubmittedExercises((prev) => [...prev, exercise]);
    }

    const getExercises = useCallback(async () => {
        const response = await apiRequest(`/api/exercises?class_id=${classId}`, 'GET');
        const submitted = response.data.filter((exercise) => exercise.submitted);
        const unsubmitted = response.data.filter((exercise) => !exercise.submitted);
        setUnsubmittedExercises(unsubmitted);
        setSubmittedExercises(submitted);
    }, [classId, apiRequest]);

    useEffect(() => {
        getExercises();
    }, [getExercises]);

    useEffect(() => {
        async function checkIfTeacher() {
            const response = await apiRequest(`/api/classes/is-teacher/${classId}`, 'GET');
            setIsTeacher(response.is_teacher);
        }

        checkIfTeacher();
    }, [classId, apiRequest]);

    return (
        <div className="container-md">
            <h1>{t('pages.classes.exercise_list.title')}</h1>
            <CardList>
                {unsubmittedExercises.length === 0 && (
                    <p className="no-assignments">{t('pages.classes.exercise_list.none')}</p>
                )}

                {unsubmittedExercises.map((exercise) => (
                    <ExerciseCard
                        key={exercise.exercise_id}
                        exerciseId={exercise.exercise_id}
                        isGenerated={exercise.is_ai_generated}
                        isSubmitted={false}
                        isSolved={exercise.is_solved}
                        isHidden={exercise.is_hidden}
                        isTeacher={isTeacher}
                        title={exercise.title}
                        onSubmit={() => handleSubmit(exercise)}
                        refresh={getExercises}
                        learningObjectives={exercise.learning_objectives}
                    >
                        {exercise.request}
                    </ExerciseCard>
                ))}
            </CardList>

            <h1 className="mt-3">{t('pages.classes.exercise_list.archived')}</h1>
            <CardList>
                {submittedExercises.length === 0 && (
                    <p>{t('pages.classes.exercise_list.archived_none')}</p>
                )}

                {submittedExercises.map((exercise) => (
                    <ExerciseCard
                        key={exercise.exercise_id}
                        exerciseId={exercise.exercise_id}
                        isGenerated={exercise.is_ai_generated}
                        isHidden={exercise.is_hidden}
                        isSolved={exercise.is_solved}
                        isSubmitted={true}
                        isTeacher={isTeacher}
                        learningObjectives={exercise.learning_objectives}
                        title={exercise.title}
                        onUnsubmit={() => handleUnsubmit(exercise)}
                        refresh={getExercises}
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
                        classId={classId}
                    />
                </>
            )}
        </div>
    );
}

export default ExerciseList;
