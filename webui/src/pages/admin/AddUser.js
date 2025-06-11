import ButtonModal from '../../components/ButtonModal';
import useAuth from '../../hooks/useAuth';
import { useState } from 'react';

// Button to add a new user + modal to fill in the details
function AddUser({ refreshUsers }) {
    const { apiRequest } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    async function handleAddUser() {
        const result = await apiRequest('/api/auth/register', 'POST', {
            'username': username,
            'password': password,
            'is_teacher': false,
            'is_admin': false,
        });

        if (result.success) {
            refreshUsers();
        } else {
            alert(result.data.message || 'Failed to add user');
        }
    }
    return (
        <ButtonModal
            className="btn btn-success"
            title="Add User"
            buttonText="Add New User"
            footerButtons={[
                {
                    text: 'Save',
                    variant: 'primary',
                    onClick: handleAddUser,
                    autoClose: true,
                    disabled: !username || !password,
                },
            ]}
        >
            <div className="mb-3">
                <label className="form-label">Username</label>
                <input type="text" className="form-control" defaultValue={username} onInput={(e) => setUsername(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Password</label>
                <input type="text" className="form-control" defaultValue={password} onInput={(e) => setPassword(e.target.value)} />
            </div>
        </ButtonModal>
    );
}

export default AddUser;