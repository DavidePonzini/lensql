import { useState, useEffect, useCallback } from 'react';
import useAuth from '../../hooks/useAuth';
import { useParams } from 'react-router-dom';

import ExerciseCard from './ExerciseCard';
import CardList from '../../components/CardList';
import ExerciseAdd from './ExerciseAdd';


function ExerciseList() {
    const { classId } = useParams();
    const { apiRequest } = useAuth();

    const [isTeacher, setIsTeacher] = useState(false);
    const [unsubmittedExercises, setUnsubmittedExercises] = useState([]);
    const [submittedExercises, setSubmittedExercises] = useState([]);

    function handleSubmit(exercise) {
        setUnsubmittedExercises((prevExercises) => prevExercises.filter((e) => e.id !== exercise.id));
        setSubmittedExercises((prevExercises) => [...prevExercises, exercise]);
    }

    function handleUnsubmit(exercise) {
        setSubmittedExercises((prevExercises) => prevExercises.filter((e) => e.id !== exercise.id));
        setUnsubmittedExercises((prevExercises) => [...prevExercises, exercise]);
    }

    const getExercises = useCallback(async () => {
        const response = await apiRequest(`/api/exercises?class_id=${classId}`, 'GET');

        const submitted = response.data.filter((exercise) => { return exercise.submitted });
        const unsubmitted = response.data.filter((exercise) => { return !exercise.submitted });
        setUnsubmittedExercises(unsubmitted);
        setSubmittedExercises(submitted);
    }, [classId, apiRequest]);

    useEffect(() => {
        getExercises();
    }, [getExercises]);

    useEffect(() => {
        async function checkIfTeacher() {
            const response = await apiRequest(`/api/classes/is-teacher?class_id=${classId}`, 'GET');

            setIsTeacher(response.is_teacher);
        }

        checkIfTeacher();
    }, [classId, apiRequest]);

    return (
        <div className="container-md">
            <h1>Exercises</h1>
            <CardList>
                {unsubmittedExercises.length === 0 && <p className="no-assignments">No exercises</p>}

                {unsubmittedExercises.map((exercise) => {
                    return (
                        <ExerciseCard
                            key={exercise.exercise_id}
                            exerciseId={exercise.exercise_id}
                            isGenerated={exercise.is_ai_generated}
                            isSubmitted={false}
                            isHidden={exercise.is_hidden}
                            isTeacher={isTeacher}
                            title={exercise.title}
                            onSubmit={() => handleSubmit(exercise)}
                            refresh={getExercises}
                            learningObjectives={exercise.learning_objectives}
                        >
                            {exercise.request}
                        </ExerciseCard>
                    );
                })}
            </CardList>

            <h1 className="mt-3">Archived</h1>
            <CardList>
                {submittedExercises.length === 0 && <p>No archived exercises</p>}

                {submittedExercises.map((exercise) => {
                    return (
                        <ExerciseCard
                            key={exercise.exercise_id}
                            exerciseId={exercise.exercise_id}
                            isGenerated={exercise.is_ai_generated}
                            isHidden={exercise.is_hidden}
                            isSubmitted={true}
                            isTeacher={isTeacher}
                            learningObjectives={exercise.learning_objectives}
                            title={exercise.title}
                            onUnsubmit={() => handleUnsubmit(exercise)}
                            refresh={getExercises}
                        >
                            {exercise.request}
                        </ExerciseCard>
                    );
                })}
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