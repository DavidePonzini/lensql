import { useEffect, useState } from 'react';
import useAuth from '../../hooks/useAuth';
import Table from 'react-bootstrap/Table';
import ButtonModal from '../../components/ButtonModal';
import AssignStudents from './AssignStudents';

function Users() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const { apiRequest, userInfo } = useAuth();

    async function handleToggleTeacher(username, value) {
        await apiRequest('/api/admin/set-teacher', 'POST', {
            username: username,
            value: value
        });

        setUsers((prevUsers) => {
            return prevUsers.map((user) => {
                if (user.username === username) {
                    return { ...user, is_teacher: value };
                }
                return user;
            });
        }
        );
    }

    async function handleToggleAdmin(username, value) {
        await apiRequest('/api/admin/set-admin', 'POST', {
            username: username,
            value: value
        });

        setUsers((prevUsers) => {
            return prevUsers.map((user) => {
                if (user.username === username) {
                    return { ...user, is_admin: value };
                }
                return user;
            });
        }
        );
    }

    useEffect(() => {
        async function fetchUsers() {
            const response = await apiRequest('/api/admin/users', 'GET')

            setUsers(response.data);
            setLoading(false);
        }
        fetchUsers();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps


    if (loading) {
        return <p>Loading...</p>;
    }

    return (
        <div className="row">
            <div className="col">
                <Table striped bordered hover>
                    <thead className='table-dark'>
                        <tr>
                            <th>Username</th>
                            <th>Teacher</th>
                            <th>Admin</th>
                            <th style={{ width: '100px' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.username}>
                                <td>{user.username}</td>
                                <td>
                                    <input type='checkbox'
                                        checked={user.is_teacher}
                                        onChange={(e) => handleToggleTeacher(user.username, e.target.checked)}
                                    />
                                </td>
                                <td>
                                    <input type='checkbox'
                                        checked={user.is_admin}
                                        onChange={(e) => handleToggleAdmin(user.username, e.target.checked)}
                                        disabled={userInfo.username === user.username} // Disable toggle for current user
                                    />
                                </td>
                                <td>
                                    {user.is_teacher && (
                                        <ButtonModal
                                            className="btn btn-secondary btn-sm"
                                            title="Set Students"
                                            buttonText="Students"
                                        >
                                            <AssignStudents teacher={user.username} />
                                        </ButtonModal>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </div>
        </div>
    );
}

export default Users;