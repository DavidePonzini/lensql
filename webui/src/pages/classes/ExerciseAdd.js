import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import ExerciseMask from './ExerciseMask';

function ExerciseAdd({ refresh, classId }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [exerciseTitle, setExerciseTitle] = useState('');
    const [exerciseRequest, setExerciseRequest] = useState('');
    const [exerciseAnswer, setExerciseAnswer] = useState('');

    async function handleAddExercise() {
        await apiRequest('/api/exercises', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'solution': exerciseAnswer,
            'class_id': classId,
        });

        refresh();
    }

    return (
        <ButtonModal
            className="btn btn-success"
            title={t('pages.classes.exercise_add.title')}
            buttonText={t('pages.classes.exercise_add.button_text')}
            footerButtons={[
                {
                    text: t('pages.classes.exercise_add.save'),
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
                answer={exerciseAnswer}
                setAnswer={setExerciseAnswer}
            />
        </ButtonModal>
    );
}

export default ExerciseAdd;
