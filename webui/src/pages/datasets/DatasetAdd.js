import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';
import DatasetMask from './DatasetMask';

function DatasetAdd({ refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();
    const [title, setTitle] = useState('');
    const [dataset, setDataset] = useState('');

    async function handleAdd() {
        await apiRequest('/api/datasets', 'POST', {
            'title': title,
            'dataset': dataset,
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
                dataset={dataset}
                setDataset={setDataset}
            />
        </ButtonModal>
    );
}

export default DatasetAdd;
