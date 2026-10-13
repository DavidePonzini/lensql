import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PasswordInput from '../../components/PasswordInput';
import useAuth from '../../hooks/useAuth';

function ChangeUserPassword() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState(null);
    const key = 'pages.admin.change_password';

    async function submit(event) {
        event.preventDefault();
        if (busy || !username.trim() || !password) return;
        setBusy(true);
        setMessage(null);
        try {
            const response = await apiRequest('/api/auth/admin/change-password', 'POST', {
                username: username.trim(), new_password: password,
            });
            setMessage({
                type: response.success ? 'success' : 'danger',
                text: response.success ? t(`${key}.success`, { username: username.trim() })
                    : response.message || t(`${key}.error`),
            });
            if (response.success) setPassword('');
        } catch {
            setMessage({ type: 'danger', text: t(`${key}.error`) });
        } finally {
            setBusy(false);
        }
    }

    return (
        <>
            <h2>{t(`${key}.title`)}</h2>
            {message && <div role="alert" className={`alert alert-${message.type}`}>{message.text}</div>}
            <form onSubmit={submit} className="row g-3">
                <div className="col-md-6">
                    <label htmlFor="admin-password-username" className="form-label">{t('pages.admin.add_user.username_label')}</label>
                    <input id="admin-password-username" name="username" className="form-control"
                        value={username} onChange={event => setUsername(event.target.value)}
                        autoComplete="off" required disabled={busy} />
                </div>
                <div className="col-md-6">
                    <label htmlFor="admin-new-password" className="form-label">{t(`${key}.password`)}</label>
                    <PasswordInput id="admin-new-password" name="new_password" value={password}
                        onChange={event => setPassword(event.target.value)} autoComplete="new-password"
                        required disabled={busy} />
                </div>
                <div className="col-12">
                    <button type="submit" className="btn btn-primary"
                        disabled={busy || !username.trim() || !password}>{t(`${key}.submit`)}</button>
                </div>
            </form>
        </>
    );
}

export default ChangeUserPassword;
