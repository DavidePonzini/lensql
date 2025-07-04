import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import ExerciseMask from './ExerciseMask';

// Button to add a new exercise + modal to fill in the details
function AddExercise({ refreshAssignments, classId }) {
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
            'class_id': classId,
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
            <ExerciseMask
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