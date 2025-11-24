import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import DatasetMask from './DatasetMask';

function DatasetUpdate({ datasetId, refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [dataset, setDataset] = useState('');

    async function handleEditDataset() {
        await apiRequest('/api/datasets', 'PUT', {
            'dataset_id': datasetId,
            'title': title,
            'dataset': dataset,
        });

        refresh();
    }

    const getDatasetData = useCallback(async () => {
        if (!datasetId) return;

        const result = await apiRequest(`/api/datasets/get/${datasetId}`, 'GET');
        setTitle(result.data.title);
        setDataset(result.data.dataset_str);
    }, [datasetId, apiRequest]);

    useEffect(() => {
        getDatasetData();
    }, [getDatasetData]);

    return (
        <ButtonModal
            className={className}
            title={t('pages.datasets.dataset_update.modal_title')}
            buttonText={t('pages.datasets.dataset_update.button_text')}
            size="lg"
            footerButtons={[
                {
                    text: t('pages.datasets.dataset_update.save'),
                    variant: 'primary',
                    onClick: handleEditDataset,
                    autoClose: true,
                },
            ]}
        >
            <DatasetMask
                title={title}
                setTitle={setTitle}
                dataset={dataset}
                setDataset={setDataset}
            />
        </ButtonModal>
    );
}

export default DatasetUpdate;
