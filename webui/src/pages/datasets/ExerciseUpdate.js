import useAuth from '../../hooks/useAuth';
import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import ExerciseMask from './ExerciseMask';

import ButtonModal from '../../components/buttons/ButtonModal';

function ExerciseUpdate({ exerciseId, refreshExercises, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [request, setRequest] = useState('');
    const [solutions, setSolutions] = useState([]);
    const [searchPath, setSearchPath] = useState('');

    async function handleEditExercise() {
        // remove empty solutions
        const filteredSolutions = solutions.filter(sol => sol.trim() !== '');

        await apiRequest('/api/exercises', 'PUT', {
            'exercise_id': exerciseId,
            'title': title,
            'request': request,
            'solutions': JSON.stringify(filteredSolutions),
            'search_path': searchPath,
        });

        refreshExercises();
    }

    const getExerciseData = useCallback(async () => {
        if (!exerciseId) return;

        const result = await apiRequest(`/api/exercises/get/${exerciseId}`, 'GET');

        console.log('Fetched exercise data:', result);

        setTitle(result.data.title);
        setRequest(result.data.request);
        setSolutions(result.data.solutions);
        setSearchPath(result.data.search_path);
    }, [exerciseId, apiRequest]);

    useEffect(() => {
        getExerciseData();
    }, [getExerciseData]);

    return (
        <ButtonModal
            className={className}
            title={t('pages.datasets.exercise_update.title')}
            buttonText={t('pages.datasets.exercise_update.button')}
            footerButtons={[
                {
                    text: t('pages.datasets.exercise_update.save'),
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
                solutions={solutions}
                setSolutions={setSolutions}
                searchPath={searchPath}
                setSearchPath={setSearchPath}
            />
        </ButtonModal>
    );
}

export default ExerciseUpdate;
