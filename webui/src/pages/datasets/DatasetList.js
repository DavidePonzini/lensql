import { useState, useEffect, useCallback, useRef } from 'react';
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
    const [loading, setLoading] = useState(true);
    const importInputRef = useRef(null);

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

    async function handleImportDataset(event) {
        const file = event.target.files?.[0];
        event.target.value = '';

        if (!file) return;

        const payload = await file.text();
        const result = await apiRequest('/api/datasets/import', 'POST', { payload });

        if (!result.success) {
            alert(result.message);
            return;
        }

        getDatasets();
    }

    const getDatasets = useCallback(async () => {
        setLoading(true);
        const response = await apiRequest('/api/datasets', 'GET');

        const sortedDatasets = (response.data ?? []).slice().sort((a, b) => {
            const aSpecial = !/^[a-zA-Z0-9]+$/i.test(a.dataset_id);
            const bSpecial = !/^[a-zA-Z0-9]+$/i.test(b.dataset_id);

            // Special datasets are sorted by dataset_id
            if (aSpecial && bSpecial) {
                return (a.dataset_id > b.dataset_id) - (a.dataset_id < b.dataset_id);
            }

            // Special datasets come before regular datasets
            if (aSpecial !== bSpecial) {
                return aSpecial ? -1 : 1;
            }

            // Regular datasets are sorted by date, newest first
            const dateA = new Date(a.joined_ts);
            const dateB = new Date(b.joined_ts);
            return dateB - dateA;
        });

        setDatasets(sortedDatasets);
        setLoading(false);
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

                <input
                    ref={importInputRef}
                    type="file"
                    accept="application/json,.json"
                    onChange={handleImportDataset}
                    className="d-none"
                />

                <Button
                    variant="success"
                    onClick={() => importInputRef.current?.click()}
                    className="me-2 mb-2"
                >
                    <i className="fa fa-file-import me-1"></i>
                    {t('pages.datasets.dataset_list.import')}
                </Button>

                <Button variant="primary" onClick={handleJoinDataset} className="me-2 mb-2">
                    <i className="fa fa-arrow-right-to-bracket me-1"></i>
                    {t('pages.datasets.dataset_list.join')}
                </Button>
            </div>

            <hr />

            <CardList>
                {datasets.length === 0 && !loading && (
                    <p>{t('pages.datasets.dataset_list.empty')}</p>
                )}

                {loading && (
                    <p className="loading">{t('pages.datasets.dataset_list.loading')}</p>
                )}

                {datasets.map((dataset) => (
                    <DatasetCard
                        key={dataset.dataset_id}
                        title={dataset.title}
                        description={dataset.description}
                        datasetId={dataset.dataset_id}
                        isOwner={dataset.is_owner}
                        participants={dataset.participants}
                        exercises={dataset.exercises}
                        queriesUser={dataset.queries_user}
                        queriesStudents={dataset.queries_students}
                        refreshDatasets={getDatasets}
                        dbms={dataset.dbms}
                    />
                ))}
            </CardList>
        </div>
    );
}

export default DatasetList;
