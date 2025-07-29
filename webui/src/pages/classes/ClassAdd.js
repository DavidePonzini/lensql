import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';
import ClassMask from './ClassMask';

function ClassAdd({ refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();
    const [title, setTitle] = useState('');
    const [dataset, setDataset] = useState('');

    async function handleAdd() {
        await apiRequest('/api/classes', 'POST', {
            'title': title,
            'dataset': dataset,
        });

        refresh();
    }

    return (
        <ButtonModal
            className={className}
            title={t('pages.classes.class.new')}
            size='lg'
            buttonText={
                <span>
                    <i className="fa fa-plus me-1"></i> {t('pages.classes.class.new')}
                </span>
            }
            footerButtons={[
                {
                    text: t('pages.classes.class.save'),
                    variant: 'primary',
                    onClick: handleAdd,
                    autoClose: true,
                    disabled: !title,
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

export default ClassAdd;
