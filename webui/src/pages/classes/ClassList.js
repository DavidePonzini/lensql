import { useState, useEffect, useCallback } from 'react';
import useAuth from '../../hooks/useAuth';

import ClassCard from './ClassCard';
import CardList from '../../components/CardList';
import { Button } from 'react-bootstrap';
import ClassAdd from './ClassAdd';

function ClassList() {
    const { apiRequest } = useAuth();

    const [classes, setClasses] = useState([]);

    async function handleJoinClass() {
        const joinCode = prompt('Enter class join code:');
        joinCode?.trim().toUpperCase();
        if (!joinCode) {
            return;
        }

        const result = await apiRequest('/api/classes/join', 'POST', {
            'class_id': joinCode,
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
            <h1>My Classes</h1>
            <CardList>
                {classes.length === 0 && <p>Nothing here. Join a class to see exercises.</p>}

                {classes.map((cl) => {
                    return (
                        <ClassCard
                            title={cl.title}
                            classId={cl.class_id}
                            isTeacher={cl.is_teacher}
                            participants={cl.participants}
                            exercises={cl.exercises}
                            queries={cl.queries}
                            refreshClasses={getClasses}
                            key={cl.class_id}
                        />
                    );
                })}
            </CardList>

            <hr />
            <Button variant="primary" onClick={handleJoinClass} className="me-2 mb-2">
                <i className="fa fa-plus me-1"></i>
                Join Class
            </Button>

            <ClassAdd
                refresh={getClasses}
                className="btn btn-secondary me-2 mb-2"
            />
        </div>
    );
}

export default ClassList;