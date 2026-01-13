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

        const sortedDatasets = (response.data ?? []).slice().sort((a, b) => {
            const aSpecial = !/^[a-zA-Z0-9]+$/i.test(a.dataset_id);
            const bSpecial = !/^[a-zA-Z0-9]+$/i.test(b.dataset_id);

            if (aSpecial !== bSpecial) {
                return aSpecial ? -1 : 1;
            }

            return (a.dataset_id.toLowerCase() > b.dataset_id.toLowerCase()) - (a.dataset_id.toLowerCase() < b.dataset_id.toLowerCase());
        });

        setDatasets(sortedDatasets);
    }, [apiRequest]);

    useEffect(() => {
        getDatasets();
    }, [getDatasets]);

    return (
        <div className="container-md">
            <h1 className=''>{t('pages.datasets.dataset_list.title')}</h1>
            
            <div className='mt-4'>
                <DatasetAdd
                    refresh={getDatasets}
                    className="btn btn-success me-2 mb-2"
                />

                <Button variant="primary" onClick={handleJoinDataset} className="me-2 mb-2">
                    <i className="fa fa-arrow-right-to-bracket me-1"></i>
                    {t('pages.datasets.dataset_list.join')}
                </Button>
            </div>

            <hr />

            <CardList>
                {datasets.length === 0 && (
                    <p>{t('pages.datasets.dataset_list.empty')}</p>
                )}

                {datasets.map((cl) => (
                    <DatasetCard
                        key={cl.dataset_id}
                        title={cl.title}
                        description={cl.description}
                        datasetId={cl.dataset_id}
                        isOwner={cl.is_owner}
                        participants={cl.participants}
                        exercises={cl.exercises}
                        queriesUser={cl.queries_user}
                        queriesStudents={cl.queries_students}
                        refreshDatasets={getDatasets}
                    />
                ))}
            </CardList>
        </div>
    );
}

export default DatasetList;
