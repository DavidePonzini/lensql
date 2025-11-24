import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import ExerciseMask from './ExerciseMask';

function ExerciseAdd({ refresh, datasetId }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [exerciseTitle, setExerciseTitle] = useState('');
    const [exerciseRequest, setExerciseRequest] = useState('');
    const [exerciseSolutions, setExerciseSolutions] = useState([]);

    async function handleAddExercise() {
        // remove empty solutions
        const filteredSolutions = exerciseSolutions.filter(sol => sol.trim() !== '');

        await apiRequest('/api/exercises', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'solutions': JSON.stringify(filteredSolutions),
            'dataset_id': datasetId,
        });

        refresh();
    }

    return (
        <ButtonModal
            className="btn btn-success"
            title={t('pages.datasets.exercise_add.title')}
            buttonText={t('pages.datasets.exercise_add.button_text')}
            footerButtons={[
                {
                    text: t('pages.datasets.exercise_add.save'),
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
                solutions={exerciseSolutions}
                setSolutions={setExerciseSolutions}
            />
        </ButtonModal>
    );
}

export default ExerciseAdd;
