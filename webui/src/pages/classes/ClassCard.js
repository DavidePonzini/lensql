import { NavLink } from 'react-router-dom';
import { Button, Card } from 'react-bootstrap';
import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';
import ButtonModal from '../../components/ButtonModal';

function ClassCard({ title, classId, isTeacher = false, refreshClasses }) {
    const { apiRequest } = useAuth();

    async function getMembers() {
        const response = await apiRequest('/api/classes/members', 'GET', {
            'class_id': classId,
        });

        return response.data;
    }

    async function handleLeave() {
        await apiRequest('/api/classes/leave', 'POST', {
            'class_id': classId,
        });

        refreshClasses();
    }


    async function makeTeacher(username, value) {
        await apiRequest('/api/classes/set-teacher', 'POST', {
            'class_id': classId,
            'username': username,
            'value': value,
        });
    }

    async function handleEdit() {
        const newTitle = prompt('Enter new class name:', title);
        if (!newTitle) {
            return;
        }

        const result = await apiRequest('/api/classes/', 'PUT', {
            'title': newTitle,
            'class_id': classId,
        });

        if (!result.success) {
            alert(result.message);
            return;
        }

        refreshClasses();
    }

    return (
        <Card className="my-2">
            <Card.Header>
                <h5 className="card-title">{title}</h5>
            </Card.Header>

            <Card.Body>
                <Card.Text>
                    <strong>Join Code:</strong> {classId}
                </Card.Text>
            </Card.Body>

            <Card.Footer>
                <NavLink
                    to={classId}
                    className="btn btn-primary me-2"
                >
                    Open
                </NavLink>

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
                            />
                        </ButtonModal>

                        <Button
                            variant="secondary"
                            onClick={handleEdit}
                            className='me-2'
                        >
                            <i className="fa fa-edit"></i>
                            Edit
                        </Button>
                    </>
                )}
            </Card.Footer>
        </Card>
    );
}

export default ClassCard;