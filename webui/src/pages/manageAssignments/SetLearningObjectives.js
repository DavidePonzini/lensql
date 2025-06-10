import useAuth from '../../hooks/useAuth';
import { useEffect, useState } from 'react';

function SetLearningObjectives({ exerciseId }) {
    const { apiRequest } = useAuth();
    const [learningObjectives, setLearningObjectives] = useState([]);
    const [selectAll, setSelectAll] = useState(false);

    async function handleSetLearningObjectives(objective, value) {
        await apiRequest('/api/exercises/objective', 'POST', {
            'exercise_id': exerciseId,
            'objective': objective.objective,
            'value': value,
        });

        setLearningObjectives((prev) =>
            prev.map((o) =>
                o.objective === objective.objective ? { ...o, is_set: value } : o
            )
        );
    }

    async function handleSelectAll(value) {
        setSelectAll(value);
        // Update UI optimistically
        setLearningObjectives((prev) =>
            prev.map((o) => ({ ...o, is_set: value }))
        );
        // Send requests for all students
        await Promise.all(
            learningObjectives.map((o) =>
                apiRequest('/api/exercises/objective', 'POST', {
                    'exercise_id': exerciseId,
                    'objective': o.objective,
                    'value': value,
                })
            )
        );
    }

    useEffect(() => {
        async function fetchObjectives() {
            const data = await apiRequest(`/api/exercises/list-objectives?exercise_id=${exerciseId}`, 'GET');
            setLearningObjectives(data.data);
        }

        fetchObjectives();
    }, [exerciseId]); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        const allAssigned = learningObjectives.length > 0 && learningObjectives.every((o) => o.is_set);
        setSelectAll(allAssigned);
    }, [learningObjectives]);

    return (
        <div className="mb-3">
            <label className="form-label">Set Learning Objectives</label>

            {learningObjectives.length > 0 && (
                <div className="form-check mb-2">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        id="select-all"
                        checked={selectAll}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="select-all">
                        Select All
                    </label>
                </div>
            )}

            {learningObjectives.map((o) => (
                <div key={o.objective} className="form-check">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        checked={o.is_set}
                        id={`objective-${o.objective}`}
                        onChange={(e) => handleSetLearningObjectives(o, e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor={`objective-${o.objective}`}>
                        <b>{o.objective}</b> <i className='fw-lighter'>({o.description})</i>
                    </label>
                </div>
            ))}
        </div>
    );
}

export default SetLearningObjectives;