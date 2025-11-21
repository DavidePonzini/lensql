import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from 'react-bootstrap';

import useAuth from '../../hooks/useAuth';

import CardList from '../../components/CardList';

import DatasetCard from './DatasetCard';
import DatasetAdd from './DatasetAdd';

function DatasetList() {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [datasets, setDatasets] = useState([]);

    async function handleJoinDataset() {
        const joinCode = prompt(t('pages.datasets.dataset_list.join_prompt'));
        const code = joinCode?.trim().toUpperCase();

        if (!code) return;

        const result = await apiRequest('/api/datasets/join', 'POST', {
            'dataset_id': code,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        getDatasets();
    }

    const getDatasets = useCallback(async () => {
        const response = await apiRequest('/api/datasets', 'GET');
        setDatasets(response.data);
    }, [apiRequest]);

    useEffect(() => {
        getDatasets();
    }, [getDatasets]);

    return (
        <div className="container-md">
            <h1>{t('pages.datasets.dataset_list.title')}</h1>
            <CardList>
                {datasets.length === 0 && (
                    <p>{t('pages.datasets.dataset_list.empty')}</p>
                )}

                {datasets.map((cl) => (
                    <DatasetCard
                        key={cl.dataset_id}
                        title={cl.title}
                        datasetId={cl.dataset_id}
                        isTeacher={cl.is_teacher}
                        participants={cl.participants}
                        exercises={cl.exercises}
                        queries={cl.queries}
                        refreshDatasets={getDatasets}
                    />
                ))}
            </CardList>

            <p>{t('pages.datasets.dataset_list.new_dataset_suggestion')}</p>

            <hr />
            <Button variant="primary" onClick={handleJoinDataset} className="me-2 mb-2">
                <i className="fa fa-plus me-1"></i>
                {t('pages.datasets.dataset_list.join')}
            </Button>

            <DatasetAdd
                refresh={getDatasets}
                className="btn btn-secondary me-2 mb-2"
            />
        </div>
    );
}

export default DatasetList;
