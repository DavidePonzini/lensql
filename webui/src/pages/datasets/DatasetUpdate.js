import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import DatasetMask from './DatasetMask';

function DatasetUpdate({ datasetId, refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dataset, setDataset] = useState('');
    const [searchPath, setSearchPath] = useState('');
    const [dbms, setDbms] = useState('');

    async function handleEditDataset() {
        await apiRequest('/api/datasets', 'PUT', {
            'dataset_id': datasetId,
            'title': title,
            'description': description,
            'dataset': dataset,
            'search_path': searchPath,
            'dbms': dbms,
        });

        refresh();
    }

    const getDatasetData = useCallback(async () => {
        if (!datasetId) return;

        const result = await apiRequest(`/api/datasets/get/${datasetId}`, 'GET');
        setTitle(result.data.title);
        setDescription(result.data.description);
        setDataset(result.data.dataset_str);
        setSearchPath(result.data.search_path);
        setDbms(result.data.dbms);
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
                description={description}
                setDescription={setDescription}
                dataset={dataset}
                setDataset={setDataset}
                searchPath={searchPath}
                setSearchPath={setSearchPath}
                dbms={dbms}
                setDbms={setDbms}
            />
        </ButtonModal>
    );
}

export default DatasetUpdate;
