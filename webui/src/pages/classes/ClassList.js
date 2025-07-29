import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from 'react-bootstrap';

import useAuth from '../../hooks/useAuth';

import CardList from '../../components/CardList';

import ClassCard from './ClassCard';
import ClassAdd from './ClassAdd';

function ClassList() {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [classes, setClasses] = useState([]);

    async function handleJoinClass() {
        const joinCode = prompt(t('pages.classes.class_list.join_prompt'));
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
            <h1>{t('pages.classes.class_list.title')}</h1>
            <CardList>
                {classes.length === 0 && (
                    <p>{t('pages.classes.class_list.empty')}</p>
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

            <p>{t('pages.classes.class_list.new_course_suggestion')}</p>

            <hr />
            <Button variant="primary" onClick={handleJoinClass} className="me-2 mb-2">
                <i className="fa fa-plus me-1"></i>
                {t('pages.classes.class_list.join')}
            </Button>

            <ClassAdd
                refresh={getClasses}
                className="btn btn-secondary me-2 mb-2"
            />
        </div>
    );
}

export default ClassList;
