import { NavLink } from 'react-router-dom';
import { Button, Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import ItemAssignmentList from '../../components/ItemAssignmentList';
import ButtonModal from '../../components/buttons/ButtonModal';
import ButtonShowDataset from '../../components/buttons/ButtonShowDataset';
import LearningStatsAll from '../../components/learningStats/LearningStatsAll';

import DatasetUpdate from './DatasetUpdate';

function DatasetCard({ title, datasetId, isTeacher = false, participants, exercises, queriesUser, queriesStudents, refreshDatasets }) {
    const { apiRequest, userInfo } = useAuth();
    const { t } = useTranslation();

    async function getMembers() {
        const response = await apiRequest(`/api/datasets/members/${datasetId}`, 'GET');
        return response.members.map(member => ({
            id: member.username,
            label: member.username,
            isAssigned: member.is_teacher,
        }));
    }

    async function handleLeave() {
        if (!window.confirm(t('pages.datasets.dataset_card.confirm_leave'))) {
            return;
        }

        const result = await apiRequest('/api/datasets/leave', 'POST', {
            'dataset_id': datasetId,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        refreshDatasets();
    }

    async function makeTeacher(id, value) {
        await apiRequest('/api/datasets/set-teacher', 'POST', {
            'dataset_id': datasetId,
            'username': id,
            'value': value,
        });

        refreshDatasets();
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">{title}</h5>
            </Card.Header>

            <Card.Body>
                <strong>{t('pages.datasets.dataset_card.exercises')}:</strong> {exercises}
                <br />
                <strong>{t('pages.datasets.dataset_card.queries_user')}:</strong> {queriesUser}
                <br />
                <br />
                <strong>{t('pages.datasets.dataset_card.join_code')}:</strong> {datasetId}

                {isTeacher && (
                    <>
                        <hr />
                        <span className="badge bg-success">{t('pages.datasets.dataset_card.badge_teacher')}</span>
                        <br />
                        <strong>{t('pages.datasets.dataset_card.students')}:</strong> {participants}
                        <br />
                        <strong>{t('pages.datasets.dataset_card.queries_students')}:</strong> {queriesStudents}
                    </>
                )}
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={datasetId}
                    className="btn btn-primary me-2"
                >
                    {t('pages.datasets.dataset_card.open')}
                </NavLink>

                <ButtonShowDataset
                    className="btn btn-secondary me-2"
                    datasetId={datasetId}
                    title={title}
                />

                <ButtonModal
                    className="btn btn-info me-2"
                    title={t('pages.datasets.dataset_card.my_learning_analytics')}
                    buttonText={t('pages.datasets.dataset_card.my_learning_analytics')}
                    fullscreen={true}
                >
                    <LearningStatsAll datasetId={datasetId} isTeacher={false} />
                </ButtonModal>

                {/^[a-zA-Z0-9]+$/.test(datasetId) && (
                    <Button
                        variant="danger"
                        onClick={handleLeave}
                        className='me-2'
                    >
                        {t('pages.datasets.dataset_card.leave')}
                    </Button>
                )}

                {isTeacher && (
                    <>
                        <div className='vr me-2 mb-1' style={{ verticalAlign: 'middle', height: '2.5rem' }} />

                        <DatasetUpdate
                            datasetId={datasetId}
                            title={title}
                            refresh={refreshDatasets}
                            className="btn btn-warning me-2"
                        />

                        <ButtonModal
                            className="btn btn-info me-2"
                            title={t('pages.datasets.dataset_card.student_learning_analytics')}
                            buttonText={t('pages.datasets.dataset_card.student_learning_analytics')}
                            fullscreen={true}
                        >
                            <LearningStatsAll datasetId={datasetId} isTeacher={true} />
                        </ButtonModal>


                        <ButtonModal
                            className="btn btn-warning me-2"
                            title={t('pages.datasets.dataset_card.set_teachers')}
                            buttonText={t('pages.datasets.dataset_card.set_teachers')}
                        >
                            <ItemAssignmentList
                                fetchItems={getMembers}
                                assignAction={makeTeacher}
                                title={t('pages.datasets.dataset_card.participants')}
                                disabledItems={[userInfo?.username]}
                            />
                        </ButtonModal>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default DatasetCard;
