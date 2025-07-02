import useAuth from '../../hooks/useAuth';
import { useEffect, useState, useCallback } from 'react';

import ButtonModal from '../../components/ButtonModal';

// Data placeholder for exercise data
function ExerciseUpdate({ exerciseId, refreshExercises }) {
    const { apiRequest } = useAuth();
    const [availableDatasets, setAvailableDatasets] = useState([]);
    const [loading, setLoading] = useState(true);

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

        const data = await apiRequest('/api/exercises/get', 'GET', {
            'exercise_id': exerciseId,
        });

        setTitle(data.data.title);
        setRequest(data.data.request);
        setDatasetName(data.data.dataset_name);
        setAnswer(data.data.solution);
    }, [exerciseId, apiRequest]);

    useEffect(() => {
        getExerciseData();
    }, [exerciseId, apiRequest, getExerciseData]);

    useEffect(() => {
        async function fetchDatasets() {
            const data = await apiRequest('/api/datasets/list', 'GET');
            setAvailableDatasets(data.data);
            setLoading(false);
        }

        fetchDatasets();
    }
        , [apiRequest]);

    return (
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

            <div className="mb-3">
                <label className="form-label">Title</label>
                <input type="text" className="form-control" defaultValue={title} onInput={(e) => setTitle(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Request</label>
                <textarea className="form-control" rows="3" defaultValue={request} onInput={(e) => setRequest(e.target.value)}></textarea>
            </div>
            <div className="mb-3">
                <label className="form-label">Dataset</label>
                {loading ? (
                    <p>Loading datasets...</p>
                ) : (
                    <select className="form-select" aria-label="Default select example" onChange={(e) => setDatasetName(e.target.value)} value={datasetName ? datasetName : ''}>
                        <option value=''>None</option>
                        {availableDatasets.map((dataset) => (
                            <option key={dataset} value={dataset}>
                                {dataset}
                            </option>
                        ))}
                    </select>
                )}
            </div>
            <div className="mb-3">
                <label className="form-label">Answer</label>
                <textarea className="form-control" rows="3" defaultValue={answer} onInput={(e) => setAnswer(e.target.value)}></textarea>
            </div>
        </ButtonModal>
    );
}

export default ExerciseUpdate;