import { NavLink } from 'react-router-dom';
import { Button, Card } from 'react-bootstrap';
import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';
import ButtonModal from '../../components/ButtonModal';
import ClassUpdate from './ClassUpdate';
import ButtonShowDataset from '../../components/ButtonShowDataset';

function ClassCard({ title, classId, isTeacher = false, participants, exercises, queries, refreshClasses }) {
    const { apiRequest, userInfo } = useAuth();

    async function getMembers() {
        const response = await apiRequest(`/api/classes/members?class_id=${classId}`, 'GET');

        return response.members.map(member => ({
            id: member.username,
            label: member.username,
            isAssigned: member.is_teacher,
        }));
    }

    async function handleLeave() {
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
                <strong>Exercises:</strong> {exercises}
                <br />
                <strong>Queries executed:</strong> {queries}

                {isTeacher && (
                    <>
                        <hr />
                        <span className="badge bg-success">Teacher</span>
                        <br />
                        <strong>Join Code:</strong> {classId}
                        <br />
                        <strong>Students:</strong> {participants}
                    </>
                )}
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={classId}
                    className="btn btn-primary me-2"
                >
                    Open
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
                    Leave
                </Button>

                {isTeacher && (
                    <>
                        <ButtonModal
                            className="btn btn-primary me-2"
                            title="Set Teachers"
                            buttonText="Teachers"
                        >
                            <ItemAssignmentList
                                fetchItems={getMembers}
                                assignAction={makeTeacher}
                                title='Participants'
                                disabledItems={[userInfo?.username]}  // Prevent self from being unassigned
                            />
                        </ButtonModal>

                        <ClassUpdate
                            classId={classId}
                            title={title}
                            refresh={refreshClasses}
                            className="btn btn-secondary me-2"
                        />
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ClassCard;