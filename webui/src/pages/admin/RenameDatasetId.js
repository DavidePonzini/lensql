import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';

function RenameDatasetId() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [datasetId, setDatasetId] = useState('');
    const [newId, setNewId] = useState('');
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState(null);
    const key = 'pages.admin.rename_dataset';
    const isSpecial = id => Boolean(id.trim()) && !/^[a-zA-Z0-9]+$/.test(id.trim());
    const currentIsSpecial = isSpecial(datasetId);
    const newIsSpecial = isSpecial(newId);

    async function submit(event) {
        event.preventDefault();
        setBusy(true);
        setMessage(null);
        try {
            const response = await apiRequest('/api/datasets/rename-id', 'POST', {
                dataset_id: datasetId.trim(),
                new_dataset_id: newId.trim(),
            });
            setMessage({
                type: response.success ? 'success' : 'danger',
                text: response.success
                    ? t(`${key}.success`, { id: response.dataset_id })
                    : response.message || t(`${key}.error`),
            });
            if (response.success) {
                setDatasetId(response.dataset_id);
                setNewId('');
            }
        } catch {
            setMessage({ type: 'danger', text: t(`${key}.error`) });
        } finally {
            setBusy(false);
        }
    }

    return (
        <>
            <hr className="my-4" />
            <h2>{t(`${key}.title`)}</h2>
            {message && <div role="alert" className={`alert alert-${message.type}`}>{message.text}</div>}
            <form onSubmit={submit} className="row g-3">
                <div className="col-md-6">
                    <label htmlFor="rename-current-id" className="form-label">{t(`${key}.current_id`)}</label>
                    <input id="rename-current-id" className={`form-control${currentIsSpecial ? ' border-warning bg-warning-subtle' : ''}`} value={datasetId}
                        aria-describedby={currentIsSpecial ? 'rename-current-special' : undefined}
                        onChange={event => setDatasetId(event.target.value.toUpperCase())} required disabled={busy} />
                    {currentIsSpecial && <div id="rename-current-special" className="form-text text-warning-emphasis">{t(`${key}.special`)}</div>}
                </div>
                <div className="col-md-6">
                    <label htmlFor="rename-new-id" className="form-label">{t(`${key}.new_id`)}</label>
                    <input id="rename-new-id" className={`form-control${newIsSpecial ? ' border-warning bg-warning-subtle' : ''}`} value={newId}
                        aria-describedby={newIsSpecial ? 'rename-new-special' : undefined}
                        onChange={event => setNewId(event.target.value.toUpperCase())} required disabled={busy} />
                    {newIsSpecial && <div id="rename-new-special" className="form-text text-warning-emphasis">{t(`${key}.special`)}</div>}
                </div>
                <div className="col-12">
                    <button className="btn btn-primary" type="submit"
                        disabled={busy || !datasetId.trim() || !newId.trim()}>{t(`${key}.submit`)}</button>
                </div>
            </form>
        </>
    );
}

export default RenameDatasetId;
