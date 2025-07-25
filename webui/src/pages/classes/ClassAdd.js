import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';
import ClassMask from './ClassMask';

// Button to add a new exercise + modal to fill in the details
function ClassAdd({ refresh, className }) {
    const { apiRequest } = useAuth();
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
            title="New Course"
            size='lg'
            buttonText={
                <span>
                    <i className="fa fa-plus me-1"></i> New Course
                </span>
            }
            footerButtons={[
                {
                    text: 'Save',
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