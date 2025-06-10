import ButtonModal from '../../components/ButtonModal';
import ButtonShowDataset from '../../components/ButtonShowDataset';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import AssignExercise from './AssignExercise';
import ExerciseData from './ExerciseData';
import SetLearningObjectives from './SetLearningObjectives';


// A single row in the exercise list + buttons
function ExerciseRow({ exercise, refreshAssignments }) {
    const { apiRequest } = useAuth();

    const exerciseId = exercise.id;
    const exerciseDatasetName = exercise.dataset_name;
    const [exerciseTitle, setExerciseTitle] = useState(exercise.title);
    const [exerciseRequest, setExerciseRequest] = useState(exercise.request);
    const [exerciseDatasetId, setExerciseDatasetId] = useState(exercise.dataset_id);
    const [exerciseAnswer, setExerciseAnswer] = useState(exercise.expected_answer);
    const isAiGenerated = exercise.is_ai_generated;

    async function handleEditExercise() {
        await apiRequest('/api/exercises', 'PUT', {
            'exercise_id': exerciseId,
            'title': exerciseTitle,
            'request': exerciseRequest,
            'dataset_id': exerciseDatasetId,
            'expected_answer': exerciseAnswer,
        });

        refreshAssignments();
    }

    async function handleDeleteExercise() {
        await apiRequest('/api/exercises', 'DELETE', {
            'exercise_id': exerciseId,
        });

        refreshAssignments();
    }

    return (
        <tr key={exerciseId}>
            <td>{exerciseTitle}</td>
            <td>{exerciseRequest}</td>
            <td>{exerciseAnswer}</td>
            <td>{exerciseDatasetName}</td>
            <td>
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={isAiGenerated}
                    readOnly
                />
            </td>
            <td>
                <ButtonShowDataset
                    datasetId={exerciseDatasetId}
                    className="btn-sm me-1 mb-1"
                />

                <ButtonModal
                    className="btn btn-primary btn-sm me-1 mb-1"
                    title="Assign Exercise"
                    buttonText="Assign"
                >
                    <AssignExercise exerciseId={exerciseId} />
                </ButtonModal>

                <ButtonModal
                    className="btn btn-primary btn-sm me-1 mb-1"
                    title="Set Learning Objectives"
                    buttonText="Objectives"
                >
                    <SetLearningObjectives exerciseId={exerciseId} />
                </ButtonModal>

                <ButtonModal
                    className="btn btn-warning btn-sm me-1 mb-1"
                    title="Edit Exercise"
                    buttonText="Edit"
                    footerButtons={[
                        {
                            text: 'Save',
                            variant: 'primary',
                            onClick: handleEditExercise,
                            autoClose: true,
                        },
                    ]}
                >
                    <ExerciseData
                        title={exerciseTitle}
                        setTitle={setExerciseTitle}
                        request={exerciseRequest}
                        setRequest={setExerciseRequest}
                        datasetId={exerciseDatasetId}
                        setDatasetId={setExerciseDatasetId}
                        answer={exerciseAnswer}
                        setAnswer={setExerciseAnswer}
                    />
                </ButtonModal>


                <button className='btn btn-danger btn-sm me-1 mb-1' onClick={handleDeleteExercise}>
                    Delete
                </button>
            </td>
        </tr>
    );
}

export default ExerciseRow;