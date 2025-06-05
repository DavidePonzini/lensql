import useAuth from '../../hooks/useAuth';
import { useEffect, useState } from 'react';

// Data placeholder for exercise data
function ExerciseData({ title, setTitle, request, setRequest, datasetId, setDatasetId, answer, setAnswer }) {
    const { apiRequest } = useAuth();
    const [availableDatasets, setAvailableDatasets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchDatasets() {
            const data = await apiRequest('/api/datasets/list', 'GET');
            setAvailableDatasets(data.data);
            setLoading(false);
        }

        fetchDatasets();
    }
        , []); // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <>
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
                    <select className="form-select" aria-label="Default select example" onChange={(e) => setDatasetId(e.target.value)} value={datasetId ? datasetId : ''}>
                        <option value=''>None</option>
                        {availableDatasets.map((dataset) => (
                            <option key={dataset.id} value={dataset.id}>
                                {dataset.name}
                            </option>
                        ))}
                    </select>
                )}
            </div>
            <div className="mb-3">
                <label className="form-label">Answer</label>
                <textarea className="form-control" rows="3" defaultValue={answer} onInput={(e) => setAnswer(e.target.value)}></textarea>
            </div>
        </>
    );
}

export default ExerciseData;