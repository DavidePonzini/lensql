import { useState } from 'react';
import { Button, Modal, Tabs, Tab } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';
import GenerationErrors from './GenerationErrors';
import DatasetTips from './DatasetTips';

export default function ActivityGenerate({ refresh }) {
    const { apiRequest } = useAuth();
    const { loadUserInfo } = useUserInfo();
    const { t } = useTranslation();
    const key = 'pages.activities.generate';
    const [show, setShow] = useState(false);
    const [options, setOptions] = useState(null);
    const [mode, setMode] = useState('errors');
    const [counts, setCounts] = useState({});
    const [selected, setSelected] = useState([]);
    const [students, setStudents] = useState(null);
    const [title, setTitle] = useState('');
    const [prefix, setPrefix] = useState('Exercise ');
    const [datasetMode, setDatasetMode] = useState('automatic');
    const [datasetSql, setDatasetSql] = useState('');
    const [searchPath, setSearchPath] = useState('public');
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState('');
    const total = Object.values(counts).reduce((sum, count) => sum + Number(count || 0), 0);
    async function open() {
        setShow(true);
        setOptions(null);
        setSelected([]);
        setStudents(null);
        setMessage('');
        try {
            const response = await apiRequest('/api/activities/generation-options');
            if (!response.success) throw new Error(response.message);
            setOptions(response);
        } catch (error) { setMessage(error.message || t(`${key}.error`)); }
    }
    async function generate(event) {
        event.preventDefault();
        if (busy) return;
        setBusy(true);
        setMessage('');
        try {
            const response = await apiRequest('/api/activities/generate', 'POST', {
                title, prefix,
                dataset_str: datasetMode === 'custom' ? datasetSql : null,
                ...(datasetMode === 'custom' ? { search_path: searchPath } : {}),
                errors: Object.entries(counts).filter(([, count]) => Number(count) > 0)
                    .map(([selection, count]) => {
                        const [errorId, difficulty] = selection.split(':').map(Number);
                        return { error_id: errorId, difficulty, count: Number(count) };
                    }),
            });
            if (!response.success) { setMessage(response.message); return; }
            setShow(false);
            setCounts({});
            setTitle('');
            setDatasetSql('');
            setDatasetMode('automatic');
            await refresh();
            await loadUserInfo();
        } catch { setMessage(t(`${key}.error`)); }
        finally { setBusy(false); }
    }
    async function toggleActivity(id, checked) {
        const ids = checked ? [...selected, id] : selected.filter(value => value !== id);
        setSelected(ids);
        setStudents(null);
        setMessage('');
        if (!ids.length) return;
        setBusy(true);
        try {
            const response = await apiRequest('/api/activities/generation-students', 'POST', { activity_ids: ids });
            if (response.success) setStudents(response.students);
            else setMessage(response.message);
        } catch { setMessage(t(`${key}.error`)); }
        finally { setBusy(false); }
    }
    return <>
        <Button variant="primary" className="me-2 mb-2" onClick={open}>
            <i className="fa fa-wand-magic-sparkles me-1" />{t(`${key}.button`)}
        </Button>
        <Modal show={show} onHide={() => !busy && setShow(false)} size="xl" backdrop={busy ? 'static' : true} keyboard={!busy}>
            <Modal.Header closeButton={!busy}><Modal.Title>{t(`${key}.button`)}</Modal.Title></Modal.Header>
            <Modal.Body>
                {message && <div className="alert alert-danger" role="alert">{message}</div>}
                {!options && !message && <p className="loading">{t(`${key}.loading`)}</p>}
                {options && <>
                    <p>{t(`${key}.balance`, { count: options.ai_generation_credits })}</p>
                    <Tabs activeKey={mode} onSelect={value => !busy && setMode(value)} className="mb-3">
                        <Tab eventKey="errors" title={t(`${key}.errors`)} disabled={busy}>
                            <form onSubmit={generate}>
                                <p>{t(`${key}.cost`)}</p>
                                <label className="form-label" htmlFor="generation-title">{t(`${key}.title`)}</label>
                                <input id="generation-title" className="form-control mb-3" value={title} maxLength={255} onChange={e => setTitle(e.target.value)} required disabled={busy} />
                                <label className="form-label" htmlFor="generation-prefix">{t(`${key}.prefix`)}</label>
                                <input id="generation-prefix" className="form-control mb-3" value={prefix} maxLength={240} onChange={e => setPrefix(e.target.value)} disabled={busy} />
                                <fieldset className="border rounded p-3 mb-4" disabled={busy}>
                                    <legend className="float-none w-auto px-2 fs-5">{t(`${key}.dataset_heading`)}</legend>
                                    <div className="form-check">
                                        <input id="generation-dataset-auto" className="form-check-input" type="radio" name="generation-dataset" checked={datasetMode === 'automatic'} onChange={() => setDatasetMode('automatic')} />
                                        <label className="form-check-label" htmlFor="generation-dataset-auto">{t(`${key}.dataset_auto`)}</label>
                                    </div>
                                    <div className="form-check mb-2">
                                        <input id="generation-dataset-custom" className="form-check-input" type="radio" name="generation-dataset" checked={datasetMode === 'custom'} onChange={() => setDatasetMode('custom')} />
                                        <label className="form-check-label" htmlFor="generation-dataset-custom">{t(`${key}.dataset_custom`)}</label>
                                    </div>
                                    {datasetMode === 'custom' && <>
                                        <label className="form-label" htmlFor="generation-dataset-file">{t(`${key}.dataset_file`)}</label>
                                        <input id="generation-dataset-file" className="form-control mb-2" type="file" accept=".sql,text/plain,application/sql" onChange={async event => {
                                            const file = event.target.files?.[0];
                                            event.target.value = '';
                                            if (!file) return;
                                            if (file.size > 2000000) { setMessage(t(`${key}.dataset_size`)); return; }
                                            setDatasetSql('');
                                            try { setDatasetSql(await file.text()); setMessage(''); }
                                            catch { setMessage(t(`${key}.error`)); }
                                        }} />
                                        <label className="form-label" htmlFor="generation-dataset-sql">{t(`${key}.dataset_sql`)}</label>
                                        <textarea id="generation-dataset-sql" className="form-control font-monospace mb-2" rows={11} value={datasetSql}
                                            placeholder={t('pages.activities.activity_mask.activity_str_placeholder')} onChange={event => setDatasetSql(event.target.value)} required />
                                        <DatasetTips />
                                        <label className="form-label" htmlFor="generation-search-path">{t('pages.activities.activity_mask.search_path_label')}</label>
                                        <input id="generation-search-path" className="form-control" value={searchPath} maxLength={255} onChange={event => setSearchPath(event.target.value)} required />
                                    </>}
                                </fieldset>
                                <GenerationErrors options={options} counts={counts} setCounts={setCounts} busy={busy} />
                                <div className="position-sticky bottom-0 bg-body border-top pt-3 mt-3" style={{ zIndex: 1 }}>
                                <p className="fw-semibold" aria-live="polite">{t(`${key}.total`, { count: total })}</p>
                                {total > 100 && <p className="text-danger">{t(`${key}.too_many`)}</p>}
                                {total > options.ai_generation_credits && <p className="text-danger">{t(`${key}.insufficient`)}</p>}
                                <Button type="submit" disabled={busy || !title.trim() || total < 1 || total > 100 || total > options.ai_generation_credits || (datasetMode === 'custom' && (!datasetSql.trim() || !searchPath.trim()))}>
                                    {t(`${key}.${busy ? 'generating' : 'button'}`)}
                                </Button>
                                {busy && <p role="status" className="mt-2">{t(`${key}.wait`)}</p>}
                                </div>
                            </form>
                        </Tab>
                        <Tab eventKey="students" title={t(`${key}.students_mode`)} disabled={busy}>
                            <p>{t(`${key}.students_help`)}</p>
                            {options.activities.length === 0 && <p>{t(`${key}.no_activities`)}</p>}
                            {options.activities.map(activity => <div className="form-check" key={activity.activity_id}>
                                <input className="form-check-input" id={`source-${activity.activity_id}`} type="checkbox" checked={selected.includes(activity.activity_id)} disabled={busy}
                                    onChange={e => toggleActivity(activity.activity_id, e.target.checked)} />
                                <label className="form-check-label" htmlFor={`source-${activity.activity_id}`}>{activity.title} ({activity.activity_id})</label>
                            </div>)}
                            {busy && <p role="status">{t(`${key}.loading`)}</p>}
                            {students !== null && <div className="mt-3"><h3>{t(`${key}.students`)}</h3>
                                {students.length ? <ul>{students.map(student => <li key={student}>{student}</li>)}</ul> : <p>{t(`${key}.no_students`)}</p>}
                            </div>}
                        </Tab>
                    </Tabs>
                </>}
            </Modal.Body>
        </Modal>
    </>;
}
