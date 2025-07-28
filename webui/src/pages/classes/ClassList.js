import { useState, useEffect, useCallback } from 'react';
import useAuth from '../../hooks/useAuth';

import { useTranslation } from 'react-i18next';
import ClassCard from './ClassCard';
import CardList from '../../components/CardList';
import { Button } from 'react-bootstrap';
import ClassAdd from './ClassAdd';

function ClassList() {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [classes, setClasses] = useState([]);

    async function handleJoinClass() {
        const joinCode = prompt(t('class_list.join_prompt'));
        const code = joinCode?.trim().toUpperCase();

        if (!code) return;

        const result = await apiRequest('/api/classes/join', 'POST', {
            'class_id': code,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        getClasses();
    }

    const getClasses = useCallback(async () => {
        const response = await apiRequest('/api/classes', 'GET');
        setClasses(response.data);
    }, [apiRequest]);

    useEffect(() => {
        getClasses();
    }, [getClasses]);

    return (
        <div className="container-md">
            <h1>{t('class_list.title')}</h1>
            <CardList>
                {classes.length === 0 && (
                    <>
                        <p>{t('class_list.empty_1')}</p>
                        <p>{t('class_list.empty_2')}</p>
                    </>
                )}

                {classes.map((cl) => (
                    <ClassCard
                        key={cl.class_id}
                        title={cl.title}
                        classId={cl.class_id}
                        isTeacher={cl.is_teacher}
                        participants={cl.participants}
                        exercises={cl.exercises}
                        queries={cl.queries}
                        refreshClasses={getClasses}
                    />
                ))}
            </CardList>

            <hr />
            <Button variant="primary" onClick={handleJoinClass} className="me-2 mb-2">
                <i className="fa fa-plus me-1"></i>
                {t('class_list.join')}
            </Button>

            <ClassAdd
                refresh={getClasses}
                className="btn btn-secondary me-2 mb-2"
            />
        </div>
    );
}

export default ClassList;
