import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';

function SetLearningObjectives({ exerciseId }) {
    const { apiRequest } = useAuth();

    const fetchObjectives = async () => {
        const data = await apiRequest(`/api/exercises/list-objectives?exercise_id=${exerciseId}`, 'GET');
        return data.data.map((o) => ({
            id: o.objective,
            label: (
                <>
                    <b>{o.objective}</b> <i style={{fontSize: 'smaller'}}>({o.description})</i>
                </>
            ),
            isAssigned: o.is_set,
        }));
    };

    const assignObjective = async (objectiveId, value) => {
        await apiRequest('/api/exercises/objective', 'POST', {
            exercise_id: exerciseId,
            objective: objectiveId,
            value,
        });
    };

    return (
        <ItemAssignmentList
            fetchItems={fetchObjectives}
            assignAction={assignObjective}
            title="Set Learning Objectives"
        />
    );
}

export default SetLearningObjectives;
