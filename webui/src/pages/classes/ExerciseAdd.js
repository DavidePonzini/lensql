import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import ExerciseMask from './ExerciseMask';
import { useTranslation } from 'react-i18next';

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
            title={t('exercise_add.title')}
            buttonText={t('exercise_add.button_text')}
            footerButtons={[
                {
                    text: t('exercise_add.save'),
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
