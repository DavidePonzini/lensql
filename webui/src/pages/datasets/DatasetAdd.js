import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';
import DatasetMask from './DatasetMask';

function DatasetAdd({ refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dataset, setDataset] = useState('');
    const [searchPath, setSearchPath] = useState('');
    const [dbms, setDbms] = useState('');
    const [activityStartTs, setActivityStartTs] = useState('');
    const [activityEndTs, setActivityEndTs] = useState('');

    async function handleAdd() {
        await apiRequest('/api/datasets', 'POST', {
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

    return (
        <ButtonModal
            className={className}
            title={t('pages.datasets.dataset.new')}
            size='lg'
            buttonText={
                <span>
                    <i className="fa fa-plus me-1"></i> {t('pages.datasets.dataset.new')}
                </span>
            }
            footerButtons={[
                {
                    text: t('pages.datasets.dataset.save'),
                    variant: 'primary',
                    onClick: handleAdd,
                    autoClose: true,
                    disabled: !title,
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

export default DatasetAdd;
