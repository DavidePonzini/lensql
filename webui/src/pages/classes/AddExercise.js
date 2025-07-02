import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import ExerciseUpdate from './ExerciseUpdate';
import { useParams } from 'react-router-dom';

// Button to add a new exercise + modal to fill in the details
function AddExercise({ refreshAssignments }) {
    const { classCode } = useParams();
    const { apiRequest } = useAuth();
    const [exerciseTitle, setExerciseTitle] = useState('');
    const [exerciseRequest, setExerciseRequest] = useState('');
    const [exerciseDatasetName, setExerciseDatasetName] = useState('');
    const [exerciseAnswer, setExerciseAnswer] = useState('');

    async function handleAddExercise() {
        await apiRequest('/api/exercises', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'class_code': classCode,
            'dataset_name': exerciseDatasetName,
            'solution': exerciseAnswer,
        });

        refreshAssignments();
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
            <ExerciseUpdate
                title={exerciseTitle}
                setTitle={setExerciseTitle}
                request={exerciseRequest}
                setRequest={setExerciseRequest}
                setDatasetName={setExerciseDatasetName}
                answer={exerciseAnswer}
                setAnswer={setExerciseAnswer}
            />
        </ButtonModal>
    );
}

export default AddExercise;