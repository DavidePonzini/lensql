import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import DatasetMask from './DatasetMask';

function toLocalDateTimeInput(value) {
    if (!value) return '';

    const date = new Date(value);
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return localDate.toISOString().slice(0, 16);
}

function DatasetUpdate({ datasetId, refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dataset, setDataset] = useState('');
    const [searchPath, setSearchPath] = useState('');
    const [dbms, setDbms] = useState('');
    const [activityStartTs, setActivityStartTs] = useState('');
    const [activityEndTs, setActivityEndTs] = useState('');

    async function handleEditDataset() {
        await apiRequest('/api/datasets', 'PUT', {
            'dataset_id': datasetId,
            'title': title,
            'description': description,
            'dataset': dataset,
            'search_path': searchPath,
            'dbms': dbms,
            'activity_start_ts': activityStartTs ? new Date(activityStartTs).toISOString() : '',
            'activity_end_ts': activityEndTs ? new Date(activityEndTs).toISOString() : '',
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
        setActivityStartTs(toLocalDateTimeInput(result.data.activity_start_ts));
        setActivityEndTs(toLocalDateTimeInput(result.data.activity_end_ts));
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
                activityStartTs={activityStartTs}
                setActivityStartTs={setActivityStartTs}
                activityEndTs={activityEndTs}
                setActivityEndTs={setActivityEndTs}
            />
        </ButtonModal>
    );
}

export default DatasetUpdate;
