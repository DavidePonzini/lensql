import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import ExerciseMask from './ExerciseMask';

// Button to add a new exercise + modal to fill in the details
function ExerciseAdd({ refresh, classId }) {
    const { apiRequest } = useAuth();
    const [exerciseTitle, setExerciseTitle] = useState('');
    const [exerciseRequest, setExerciseRequest] = useState('');
    const [exerciseAnswer, setExerciseAnswer] = useState('');

    async function handleAddExercise() {
        await apiRequest('/api/exercises', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'solution': exerciseAnswer,
            'class_id': classId,
        });

        refresh();
    }
    return (
        <ButtonModal
            className="btn btn-success"
            title="Add Exercise"
            buttonText="Add New Exercise"
            footerButtons={[
                {
                    text: 'Save',
                    variant: 'primary',
                    onClick: handleAddExercise,
                    autoClose: true,
                    disabled: !exerciseTitle || !exerciseRequest,
                },
            ]}
        >
            <ExerciseMask
                title={exerciseTitle}
                setTitle={setExerciseTitle}
                request={exerciseRequest}
                setRequest={setExerciseRequest}
                answer={exerciseAnswer}
                setAnswer={setExerciseAnswer}
            />
        </ButtonModal>
    );
}

export default ExerciseAdd;