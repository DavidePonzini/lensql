import { NavLink } from 'react-router-dom';
import { Button, Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';

import ItemAssignmentList from '../../components/ItemAssignmentList';
import ButtonModal from '../../components/buttons/ButtonModal';
import ButtonShowActivity from '../../components/buttons/ButtonShowActivity';
import LearningStatsAll from '../../components/learningStats/LearningStatsAll';

import ActivityUpdate from './ActivityUpdate';

function ActivityCard({
    title,
    description,
    activityId,
    isOwner = false,
    participants,
    exercises,
    queriesUser,
    queriesStudents,
    refreshActivities,
    dbms,
}) {
    const { apiRequest } = useAuth();
    const { userInfo } = useUserInfo();
    const { t } = useTranslation();

    const isTeacher = userInfo?.isTeacher || false;

    const isNew = queriesUser === 0;
    const isSpecial = !/^[a-zA-Z0-9]+$/i.test(activityId);

    async function getMembers() {
        const response = await apiRequest(`/api/activities/members/${activityId}`, 'GET');
        return response.members.map(member => ({
            id: member.username,
            label: member.username,
            isAssigned: member.is_owner,
        }));
    }

    async function handleLeave() {
        if (!window.confirm(t('pages.activities.activity_card.confirm_leave'))) {
            return;
        }

        const result = await apiRequest('/api/activities/leave', 'POST', {
            'activity_id': activityId,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        refreshActivities();
    }

    async function makeOwner(id, value) {
        await apiRequest('/api/activities/set-owner', 'POST', {
            'activity_id': activityId,
            'username': id,
            'value': value,
        });

        refreshActivities();
    }

    async function handleExport() {
        const response = await apiRequest(`/api/activities/export/${activityId}`, 'GET');

        if (!response.success) {
            alert(response.message);
            return;
        }

        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${title}.json`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    return (
        <Card className={`my-2 ${isNew ? 'border border-3 border-success' : ''}`}>
            <Card.Header>
                <h5 className="card-title">
                    {title}

                    <div className='vr mx-2 mb-1' style={{ verticalAlign: 'middle', height: '2.5rem' }} />

                    <small className='text-body-secondary'>
                        {dbms === 'postgresql' && 'PostgreSQL'}
                        {dbms === 'mysql' && 'MySQL'}
                        {dbms === 'sqlserver' && 'SQL Server'}
                        {dbms === 'oracle' && 'Oracle'}
                        {dbms === 'sqlite' && 'SQLite'}
                    </small>

                    {isSpecial && (
                        <span className="badge bg-secondary ms-2">
                            <i className="fa fa-thumbtack me-1"></i>
                            {t('pages.activities.activity_card.badge_special')}
                        </span>
                    )}

                    {isNew && (
                        <span className="badge bg-success ms-2">{t('pages.activities.activity_card.badge_new')}</span>
                    )}
                </h5>
                <h6 className="card-subtitle text-muted">{description}</h6>
            </Card.Header>

            <Card.Body>
                <strong>{t('pages.activities.activity_card.exercises')}:</strong> {exercises}
                <br />
                <strong>{t('pages.activities.activity_card.queries_user')}:</strong> {queriesUser}
                <br />
                <br />
                <strong>{t('pages.activities.activity_card.join_code')}:</strong> {activityId}

                {isOwner && isTeacher && (
                    <>
                        <hr />
                        <span className="badge bg-success">{t('pages.activities.activity_card.badge_teacher')}</span>
                        <br />
                        <strong>{t('pages.activities.activity_card.students')}:</strong> {participants}
                        <br />
                        <strong>{t('pages.activities.activity_card.queries_students')}:</strong> {queriesStudents}
                    </>
                )}
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={activityId}
                    className="btn btn-primary me-2"
                >
                    {t('pages.activities.activity_card.open')}
                </NavLink>

                <ButtonShowActivity
                    className="btn btn-secondary me-2"
                    activityId={activityId}
                    title={title}
                />

                <ButtonModal
                    className="btn btn-info me-2"
                    title={t('pages.activities.activity_card.my_learning_analytics')}
                    buttonText={t('pages.activities.activity_card.my_learning_analytics')}
                    fullscreen={true}
                >
                    <LearningStatsAll activityId={activityId} isTeacher={false} />
                </ButtonModal>

                {!isSpecial && (
                    <Button
                        variant="danger"
                        onClick={handleLeave}
                        className='me-2'
                    >
                        {t('pages.activities.activity_card.leave')}
                    </Button>
                )}

                {isOwner && (
                    <>
                        <div className='vr me-2 mb-1' style={{ verticalAlign: 'middle', height: '2.5rem' }} />

                        {isTeacher && (
                            <ButtonModal
                                className="btn btn-info me-2"
                                title={t('pages.activities.activity_card.student_learning_analytics')}
                                buttonText={t('pages.activities.activity_card.student_learning_analytics')}
                                fullscreen={true}
                            >
                                <LearningStatsAll activityId={activityId} isTeacher={true} />
                            </ButtonModal>
                        )}

                        <ActivityUpdate
                            activityId={activityId}
                            title={title}
                            refresh={refreshActivities}
                            className="btn btn-warning me-2"
                        />

                        <Button
                            variant="secondary"
                            onClick={handleExport}
                            className='me-2'
                        >
                            <i className="fa fa-file-export me-1"></i>
                            {t('pages.activities.activity_card.export')}
                        </Button>

                        <ButtonModal
                            className="btn btn-warning me-2"
                            title={t('pages.activities.activity_card.set_owners')}
                            buttonText={t('pages.activities.activity_card.set_owners')}
                        >
                            <ItemAssignmentList
                                fetchItems={getMembers}
                                assignAction={makeOwner}
                                title={t('pages.activities.activity_card.participants')}
                                disabledItems={[userInfo?.username]}
                            />
                        </ButtonModal>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ActivityCard;
