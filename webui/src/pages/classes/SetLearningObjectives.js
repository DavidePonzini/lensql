import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';

import ButtonModal from '../../components/ButtonModal';


function SetLearningObjectives({ exerciseId, refreshExercises, className }) {
    const { apiRequest } = useAuth();

    async function fetchObjectives() {
        const data = await apiRequest(`/api/exercises/objectives?exercise_id=${exerciseId}`, 'GET');
        return data.data.map((o) => ({
            id: o.objective,
            label: (
                <>
                    <b>{o.objective}</b> <i style={{ fontSize: 'smaller' }}>({o.description})</i>
                </>
            ),
            isAssigned: o.is_set,
        }));
    };

    async function assignObjective(objectiveId, value) {
        await apiRequest('/api/exercises/objectives', 'POST', {
            exercise_id: exerciseId,
            objective: objectiveId,
            value,
        });

        if (refreshExercises)
            refreshExercises();
    };

    return (
        <ButtonModal
            className={className}
            title="Set Objectives"
            buttonText="Objectives"
        >
            <ItemAssignmentList
                fetchItems={fetchObjectives}
                assignAction={assignObjective}
                title="Set Learning Objectives"
            />
        </ButtonModal>
    );
}

export default SetLearningObjectives;
