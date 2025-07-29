import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import ClassMask from './ClassMask';

function ClassUpdate({ classId, refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [dataset, setDataset] = useState('');

    async function handleEditClass() {
        await apiRequest('/api/classes', 'PUT', {
            'class_id': classId,
            'title': title,
            'dataset': dataset,
        });

        refresh();
    }

    const getClassData = useCallback(async () => {
        if (!classId) return;

        const result = await apiRequest(`/api/classes/get/${classId}`, 'GET');
        setTitle(result.data.title);
        setDataset(result.data.dataset);
    }, [classId, apiRequest]);

    useEffect(() => {
        getClassData();
    }, [getClassData]);

    return (
        <ButtonModal
            className={className}
            title={t('pages.classes.class_update.modal_title')}
            buttonText={t('pages.classes.class_update.button_text')}
            size="lg"
            footerButtons={[
                {
                    text: t('pages.classes.class_update.save'),
                    variant: 'primary',
                    onClick: handleEditClass,
                    autoClose: true,
                },
            ]}
        >
            <ClassMask
                title={title}
                setTitle={setTitle}
                dataset={dataset}
                setDataset={setDataset}
            />
        </ButtonModal>
    );
}

export default ClassUpdate;
