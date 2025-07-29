import useAuth from '../../hooks/useAuth';
import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import ButtonModal from '../../components/ButtonModal';
import ExerciseMask from './ExerciseMask';

function ExerciseUpdate({ exerciseId, refreshExercises, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [request, setRequest] = useState('');
    const [answer, setAnswer] = useState('');

    async function handleEditExercise() {
        await apiRequest('/api/exercises', 'PUT', {
            'exercise_id': exerciseId,
            'title': title,
            'request': request,
            'solution': answer,
        });

        refreshExercises();
    }

    const getExerciseData = useCallback(async () => {
        if (!exerciseId) return;

        const result = await apiRequest(`/api/exercises/get/${exerciseId}`, 'GET');

        setTitle(result.data.title);
        setRequest(result.data.request);
        setAnswer(result.data.solution);
    }, [exerciseId, apiRequest]);

    useEffect(() => {
        getExerciseData();
    }, [getExerciseData]);

    return (
        <ButtonModal
            className={className}
            title={t('pages.classes.exercise_update.title')}
            buttonText={t('pages.classes.exercise_update.button')}
            footerButtons={[
                {
                    text: t('pages.classes.exercise_update.save'),
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
                answer={answer}
                setAnswer={setAnswer}
            />
        </ButtonModal>
    );
}

export default ExerciseUpdate;
