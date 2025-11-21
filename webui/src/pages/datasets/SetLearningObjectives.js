import useAuth from '../../hooks/useAuth';
import { useTranslation } from 'react-i18next';

import ButtonModal from '../../components/buttons/ButtonModal';
import ItemAssignmentList from '../../components/ItemAssignmentList';

function SetLearningObjectives({ exerciseId, refreshExercises, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    async function fetchObjectives() {
        const data = await apiRequest(`/api/exercises/objectives?exercise_id=${exerciseId}`, 'GET');

        return data.data.map((o) => {
            const key = `learning_objectives.${o.objective_id}`;
            const label = t(`${key}.label`, o);
            const description = t(`${key}.description`, o);

            return {
                id: o.objective_id,
                label: (
                    <>
                        <b>{label}</b>{' '}
                        <i style={{ fontSize: 'smaller' }}>({description})</i>
                    </>
                ),
                isAssigned: o.is_set,
            };
        });
    }

    async function assignObjective(objectiveId, value) {
        await apiRequest('/api/exercises/objectives', 'POST', {
            exercise_id: exerciseId,
            objective_id: objectiveId,
            value,
        });

        if (refreshExercises)
            refreshExercises();
    }

    return (
        <ButtonModal
            className={className}
            title={t('pages.classes.learning_objectives.title')}
            buttonText={t('pages.classes.learning_objectives.button')}
        >
            <ItemAssignmentList
                fetchItems={fetchObjectives}
                assignAction={assignObjective}
                title={t('pages.classes.learning_objectives.list_title')}
            />
        </ButtonModal>
    );
}

export default SetLearningObjectives;
