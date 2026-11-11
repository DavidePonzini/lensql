import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from 'react-bootstrap';

import useAuth from '../../hooks/useAuth';

import CardList from '../../components/CardList';

import ActivityCard from './ActivityCard';
import ActivityAdd from './ActivityAdd';
import { Link } from 'react-router-dom';

function ActivityList() {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [activities, setActivities] = useState([]);
    const [loading, setLoading] = useState(true);
    const importInputRef = useRef(null);
    const joinedActivityIdRef = useRef(null);
    const activityCardRefs = useRef({});

    async function handleJoinActivity() {
        const joinCode = prompt(t('pages.activities.activity_list.join_prompt'));
        const code = joinCode?.trim().toUpperCase();

        if (!code) return;

        const result = await apiRequest('/api/activities/join', 'POST', {
            'activity_id': code,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        joinedActivityIdRef.current = code;
        getActivities();
    }

    async function handleImportActivity(event) {
        const file = event.target.files?.[0];
        event.target.value = '';

        if (!file) return;

        const payload = await file.text();
        const result = await apiRequest('/api/activities/import', 'POST', { payload });

        if (!result.success) {
            alert(result.message);
            return;
        }

        joinedActivityIdRef.current = result.activity_id;
        getActivities();
    }

    const getActivities = useCallback(async () => {
        setLoading(true);
        const response = await apiRequest('/api/activities', 'GET');

        const sortedActivities = (response.data ?? []).slice().sort((a, b) => {
            const aSpecial = !/^[a-zA-Z0-9]+$/i.test(a.activity_id);
            const bSpecial = !/^[a-zA-Z0-9]+$/i.test(b.activity_id);

            // Special activities are sorted by activity_id
            if (aSpecial && bSpecial) {
                return (a.activity_id > b.activity_id) - (a.activity_id < b.activity_id);
            }

            // Special activities come before regular activities
            if (aSpecial !== bSpecial) {
                return aSpecial ? -1 : 1;
            }

            // Regular activities are sorted by date, newest first
            const dateA = new Date(a.joined_ts);
            const dateB = new Date(b.joined_ts);
            return dateB - dateA;
        });

        setActivities(sortedActivities);
        setLoading(false);
    }, [apiRequest]);

    useEffect(() => {
        getActivities();
    }, [getActivities]);

    useEffect(() => {
        const joinedActivityId = joinedActivityIdRef.current;

        if (!joinedActivityId) {
            return;
        }

        const targetCard = activityCardRefs.current[joinedActivityId];

        if (!targetCard) {
            return;
        }

        targetCard.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
        });

        joinedActivityIdRef.current = null;
    }, [activities]);

    return (
        <div className="container-md">
            <h1 className=''>{t('pages.activities.activity_list.title')}</h1>

            <div className='mt-4'>
                <ActivityAdd
                    refresh={getActivities}
                    className="btn btn-success me-2 mb-2"
                />

                <input
                    ref={importInputRef}
                    type="file"
                    accept="application/json,.json"
                    onChange={handleImportActivity}
                    className="d-none"
                />

                <Button
                    variant="success"
                    onClick={() => importInputRef.current?.click()}
                    className="me-2 mb-2"
                >
                    <i className="fa fa-file-import me-1"></i>
                    {t('pages.activities.activity_list.import')}
                </Button>

                <Button variant="primary" onClick={handleJoinActivity} className="me-2 mb-2">
                    <i className="fa fa-arrow-right-to-bracket me-1"></i>
                    {t('pages.activities.activity_list.join')}
                </Button>
                <Button as={Link} role="link" to="/activities/generate" variant="primary" className="me-2 mb-2">
                    <i className="fa fa-wand-magic-sparkles me-1" />{t('pages.activities.generate.button')}
                </Button>
            </div>

            <hr />

            <CardList>
                {activities.length === 0 && !loading && (
                    <p>{t('pages.activities.activity_list.empty')}</p>
                )}

                {loading && (
                    <p className="loading">{t('pages.activities.activity_list.loading')}</p>
                )}

                {activities.map((activity) => (
                    <div
                        key={activity.activity_id}
                        ref={(element) => {
                            if (element) {
                                activityCardRefs.current[activity.activity_id] = element;
                                return;
                            }

                            delete activityCardRefs.current[activity.activity_id];
                        }}
                    >
                        <ActivityCard
                            title={activity.title}
                            description={activity.description}
                            activityId={activity.activity_id}
                            isOwner={activity.is_owner}
                            participants={activity.participants}
                            exercises={activity.exercises}
                            queriesUser={activity.queries_user}
                            queriesStudents={activity.queries_students}
                            refreshActivities={getActivities}
                            dbms={activity.dbms}
                        />
                    </div>
                ))}
            </CardList>
        </div>
    );
}

export default ActivityList;
