import useAuth from '../../hooks/useAuth';
import { useEffect, useState, useCallback } from 'react';

import ButtonModal from '../../components/ButtonModal';
import ExerciseMask from './ExerciseMask';

// Data placeholder for exercise data
function ExerciseUpdate({ exerciseId, refreshExercises, className }) {
    const { apiRequest } = useAuth();

    const [title, setTitle] = useState('');
    const [request, setRequest] = useState('');
    const [datasetName, setDatasetName] = useState('');
    const [answer, setAnswer] = useState('');

    async function handleEditExercise() {
        await apiRequest('/api/exercises', 'PUT', {
            'exercise_id': exerciseId,
            'title': title,
            'request': request,
            'dataset_name': datasetName,
            'solution': answer,
        });

        refreshExercises();
    }

    const getExerciseData = useCallback(async () => {
        if (!exerciseId) {
            return;
        }

        const result = await apiRequest(`/api/exercises/get?exercise_id=${exerciseId}`, 'GET');

        setTitle(result.data.title);
        setRequest(result.data.request);
        setDatasetName(result.data.dataset_name);
        setAnswer(result.data.solution);
    }, [exerciseId, apiRequest]);

    useEffect(() => {
        getExerciseData();
    }, [exerciseId, apiRequest, getExerciseData]);

    return (
        <ButtonModal
            className={className}
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
            <ExerciseMask
                title={title}
                setTitle={setTitle}
                request={request}
                setRequest={setRequest}
                datasetName={datasetName}
                setDatasetName={setDatasetName}
                answer={answer}
                setAnswer={setAnswer}
            />
        </ButtonModal>
    );
}

export default ExerciseUpdate;