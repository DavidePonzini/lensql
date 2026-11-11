import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ButtonModal from '../../components/buttons/ButtonModal';

import ActivityMask from './ActivityMask';

function toLocalDateTimeInput(value) {
    if (!value) return '';

    const date = new Date(value);
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return localDate.toISOString().slice(0, 16);
}

function ActivityUpdate({ activityId, refresh, className }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [activity, setActivity] = useState('');
    const [searchPath, setSearchPath] = useState('');
    const [dbms, setDbms] = useState('');
    const [activityStartTs, setActivityStartTs] = useState('');
    const [activityEndTs, setActivityEndTs] = useState('');

    async function handleEditActivity() {
        await apiRequest('/api/activities', 'PUT', {
            'activity_id': activityId,
            'title': title,
            'description': description,
            'activity': activity,
            'search_path': searchPath,
            'dbms': dbms,
            'activity_start_ts': activityStartTs ? new Date(activityStartTs).toISOString() : '',
            'activity_end_ts': activityEndTs ? new Date(activityEndTs).toISOString() : '',
        });

        refresh();
    }

    const getActivityData = useCallback(async () => {
        if (!activityId) return;

        const result = await apiRequest(`/api/activities/get/${activityId}`, 'GET');
        setTitle(result.data.title);
        setDescription(result.data.description);
        setActivity(result.data.activity_str);
        setSearchPath(result.data.search_path);
        setDbms(result.data.dbms);
        setActivityStartTs(toLocalDateTimeInput(result.data.activity_start_ts));
        setActivityEndTs(toLocalDateTimeInput(result.data.activity_end_ts));
    }, [activityId, apiRequest]);

    useEffect(() => {
        getActivityData();
    }, [getActivityData]);

    return (
        <ButtonModal
            className={className}
            title={t('pages.activities.activity_update.modal_title')}
            buttonText={t('pages.activities.activity_update.button_text')}
            size="lg"
            footerButtons={[
                {
                    text: t('pages.activities.activity_update.save'),
                    variant: 'primary',
                    onClick: handleEditActivity,
                    autoClose: true,
                },
            ]}
        >
            <ActivityMask
                title={title}
                setTitle={setTitle}
                description={description}
                setDescription={setDescription}
                activity={activity}
                setActivity={setActivity}
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

export default ActivityUpdate;
