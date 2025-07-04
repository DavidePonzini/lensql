import useAuth from '../../hooks/useAuth';
import { useState, useEffect, useCallback } from 'react';

import ButtonModal from '../../components/ButtonModal';
import ClassMask from './ClassMask';

// Data placeholder for exercise data
function ClassUpdate({ classId, refresh, className }) {
    const { apiRequest } = useAuth();

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
            if (!classId) {
                return;
            }
    
            const result = await apiRequest(`/api/classes/get?class_id=${classId}`, 'GET');
    
            setTitle(result.data.title);
            setDataset(result.data.dataset);
        }, [classId, apiRequest]);
    
        useEffect(() => {
            getClassData();
        }, [classId, apiRequest, getClassData]);

    return (
        <ButtonModal
            className={className}
            title="Edit Class"
            buttonText="Edit"
            footerButtons={[
                {
                    text: 'Save',
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