import { NavLink } from 'react-router-dom';
import { Button, Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';
import ButtonModal from '../../components/ButtonModal';
import ClassUpdate from './ClassUpdate';
import ButtonShowDataset from '../../components/ButtonShowDataset';
import LearningStatsAll from '../../components/LearningStatsAll';

function ClassCard({ title, classId, isTeacher = false, participants, exercises, queries, refreshClasses }) {
    const { apiRequest, userInfo } = useAuth();
    const { t } = useTranslation();

    async function getMembers() {
        const response = await apiRequest(`/api/classes/members/${classId}`, 'GET');
        return response.members.map(member => ({
            id: member.username,
            label: member.username,
            isAssigned: member.is_teacher,
        }));
    }

    async function handleLeave() {
        if (!window.confirm(t('class_card.confirm_leave'))) {
            return;
        }

        const result = await apiRequest('/api/classes/leave', 'POST', {
            'class_id': classId,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        refreshClasses();
    }

    async function makeTeacher(id, value) {
        await apiRequest('/api/classes/set-teacher', 'POST', {
            'class_id': classId,
            'username': id,
            'value': value,
        });

        refreshClasses();
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">{title}</h5>
            </Card.Header>

            <Card.Body>
                <strong>{t('class_card.exercises')}:</strong> {exercises}
                <br />
                <strong>{t('class_card.queries')}:</strong> {queries}

                {isTeacher && (
                    <>
                        <hr />
                        <span className="badge bg-success">{t('class_card.badge_teacher')}</span>
                        <br />
                        <strong>{t('class_card.join_code')}:</strong> {classId}
                        <br />
                        <strong>{t('class_card.students')}:</strong> {participants}
                    </>
                )}
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={classId}
                    className="btn btn-primary me-2"
                >
                    {t('class_card.open')}
                </NavLink>

                <ButtonShowDataset
                    className="btn btn-secondary me-2"
                    classId={classId}
                    title={title}
                />

                <Button
                    variant="danger"
                    onClick={handleLeave}
                    className='me-2'
                >
                    {t('class_card.leave')}
                </Button>

                {isTeacher && (
                    <>
                        <div className='vr me-2 mb-1' style={{ verticalAlign: 'middle', height: '2.5rem' }} />

                        <ButtonModal
                            className="btn btn-info me-2"
                            title={t('class_card.learning_analytics')}
                            buttonText={t('class_card.learning_analytics')}
                            fullscreen={true}
                        >
                            <LearningStatsAll classId={classId} isTeacher={isTeacher} />
                        </ButtonModal>

                        <ClassUpdate
                            classId={classId}
                            title={title}
                            refresh={refreshClasses}
                            className="btn btn-warning me-2"
                        />

                        <ButtonModal
                            className="btn btn-warning me-2"
                            title={t('class_card.set_teachers')}
                            buttonText={t('class_card.set_teachers')}
                        >
                            <ItemAssignmentList
                                fetchItems={getMembers}
                                assignAction={makeTeacher}
                                title={t('class_card.participants')}
                                disabledItems={[userInfo?.username]}
                            />
                        </ButtonModal>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ClassCard;
