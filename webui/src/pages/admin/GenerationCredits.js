import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';

export default function GenerationCredits() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [username, setUsername] = useState('');
    const [credits, setCredits] = useState('0');
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState(null);
    const key = 'pages.admin.generation_credits';
    async function submit(event) {
        event.preventDefault();
        setBusy(true);
        setMessage(null);
        try {
            const response = await apiRequest('/api/users/admin/generation-credits', 'POST', {
                username: username.trim(), ai_generation_credits: Number(credits),
            });
            setMessage({ success: response.success, text: response.success ? t(`${key}.success`) : response.message });
        } catch {
            setMessage({ success: false, text: t(`${key}.error`) });
        } finally { setBusy(false); }
    }
    return <section className="mt-4">
        <h2>{t(`${key}.title`)}</h2>
        {message && <div role="alert" className={`alert alert-${message.success ? 'success' : 'danger'}`}>{message.text}</div>}
        <form onSubmit={submit} className="row g-3">
            <div className="col-md-6">
                <label htmlFor="credits-username" className="form-label">{t('pages.admin.add_user.username_label')}</label>
                <input id="credits-username" className="form-control" value={username} onChange={e => setUsername(e.target.value)} required disabled={busy} />
            </div>
            <div className="col-md-6">
                <label htmlFor="credits-value" className="form-label">{t(`${key}.title`)}</label>
                <input id="credits-value" type="number" min="0" max="2147483647" step="1" className="form-control" value={credits} onChange={e => setCredits(e.target.value)} required disabled={busy} />
            </div>
            <div><button className="btn btn-primary" disabled={busy || !username.trim()}>{t(`${key}.save`)}</button></div>
        </form>
    </section>;
}
