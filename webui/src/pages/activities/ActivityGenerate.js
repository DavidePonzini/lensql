import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { Button, ProgressBar } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';
import GenerationErrors from './GenerationErrors';
import DatasetTips from './DatasetTips';

export default function ActivityGenerate() {
    const location = useLocation();
    const navigate = useNavigate();
    const { username } = useParams();
    const mode = location.pathname.endsWith('/students') ? 'students' : 'errors';
    const { apiRequest } = useAuth();
    const { loadUserInfo } = useUserInfo();
    const { t } = useTranslation();
    const key = 'pages.activities.generate';
    const [options, setOptions] = useState(null);
    const [counts, setCounts] = useState({});
    const selected = useMemo(() => new URLSearchParams(location.search).getAll('activity'), [location.search]);
    const studentScope = username ? location.search : '';
    const [studentsLoading, setStudentsLoading] = useState(false);
    const [students, setStudents] = useState(null);
    const [title, setTitle] = useState('');
    const [prefix, setPrefix] = useState('Exercise ');
    const [datasetMode, setDatasetMode] = useState('automatic');
    const [datasetSql, setDatasetSql] = useState('');
    const [searchPath, setSearchPath] = useState('public');
    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState(null);
    const [warning, setWarning] = useState('');
    const [progress, setProgress] = useState(null);
    const [message, setMessage] = useState('');
    const total = Object.values(counts).reduce((sum, count) => sum + Number(count || 0), 0);
    const requiredCredits = total + 1;
    useEffect(() => {
        let active = true;
        const ids = new URLSearchParams(studentScope).getAll('activity');
        setOptions(null);
        setCounts({});
        setMessage('');
        setWarning('');
        setResult(null);
        async function load() {
            try {
                const response = username
                    ? await apiRequest('/api/activities/generation-options', 'POST', { student_username: username, activity_ids: ids })
                    : await apiRequest('/api/activities/generation-options');
                if (!active) return;
                if (!response.success) throw new Error(response.message);
                setOptions(response);
            } catch (error) { if (active) setMessage(error.message || t(`${key}.error`)); }
        }
        load();
        return () => { active = false; };
    }, [apiRequest, studentScope, username, t]);
    useEffect(() => {
        let active = true;
        setStudents(null);
        setStudentsLoading(false);
        if (mode !== 'students' || !selected.length) return;
        setStudentsLoading(true);
        setMessage('');
        async function loadStudents() {
            try {
                const response = await apiRequest('/api/activities/generation-students', 'POST', { activity_ids: selected });
                if (!active) return;
                if (!response.success) throw new Error(response.message);
                setStudents(response.students);
            } catch (error) { if (active) setMessage(error.message || t(`${key}.error`)); }
            finally { if (active) setStudentsLoading(false); }
        }
        loadStudents();
        return () => { active = false; };
    }, [apiRequest, mode, selected, t]);
    function studentPath(student, ids = selected) {
        const query = new URLSearchParams();
        ids.forEach(id => query.append('activity', id));
        return `/activities/generate/students${student ? '/' + encodeURIComponent(student) : ''}?${query}`;
    }
    async function generate(event) {
        event.preventDefault();
        if (busy) return;
        setBusy(true);
        setWarning('');
        setProgress({ stage: 'preparing', total, completed: 0, failed: 0 });
        setMessage('');
        try {
            const stream = await apiRequest('/api/activities/generate', 'POST', {
                title, prefix, stream: true,
                ...(options.student_username ? { student_username: options.student_username, activity_ids: selected } : {}),
                dataset_str: datasetMode === 'custom' ? datasetSql : null,
                ...(datasetMode === 'custom' ? { search_path: searchPath } : {}),
                errors: Object.entries(counts).filter(([, count]) => Number(count) > 0)
                    .map(([selection, count]) => {
                        const [errorId, difficulty] = selection.split(':').map(Number);
                        return { error_id: errorId, difficulty, count: Number(count) };
                    }),
            }, { stream: true });
            let response;
            const consume = line => {
                if (!line.trim()) return;
                const event = JSON.parse(line);
                if (event.type === 'progress') setProgress(event);
                else response = event;
            };
            const reader = stream.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            try {
                while (true) {
                    const { value, done } = await reader.read();
                    buffer += decoder.decode(value, { stream: !done });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();
                    lines.forEach(consume);
                    if (done) break;
                }
                consume(buffer);
            } finally { reader.releaseLock(); }
            if (!response) throw new Error('Generation stream ended without a result');
            if (!response.success) { setMessage(response.message); return; }
            if (response.failed_count) {
                setWarning(t(`${key}.partial_warning`, { completed: response.generated_count, failed: response.failed_count }));
            }
            setResult(response);
            setCounts({});
            setTitle('');
            setDatasetSql('');
            setDatasetMode('automatic');
            await loadUserInfo();
        } catch { setMessage(t(`${key}.error`)); }
        finally { setBusy(false); setProgress(null); }
    }
    function toggleActivity(id, checked) {
        const ids = checked ? [...selected, id] : selected.filter(value => value !== id);
        navigate(studentPath(null, ids), { replace: true });
    }
    return <div className="container-xl pb-4">
        <Button as={Link} role="link" to="/activities" variant="link" className="px-0 mb-2" disabled={busy}>{t(`${key}.back_activities`)}</Button>
        <h1>{t(`${key}.page_title`)}</h1>
        <nav className="nav nav-tabs my-3" aria-label={t(`${key}.page_title`)}>
            <Button as={Link} role="link" to="/activities/generate" variant="link" className={`nav-link ${mode === 'errors' && !username ? 'active' : ''}`} disabled={busy}>{t(`${key}.errors`)}</Button>
            <Button as={Link} role="link" to={studentPath(null)} variant="link" className={`nav-link ${mode === 'students' || username ? 'active' : ''}`} disabled={busy}>{t(`${key}.students_mode`)}</Button>
        </nav>
        {warning && <div className="alert alert-warning" role="alert">{warning}</div>}
        {result && <div className="alert alert-success" role="status">
            <p>{t(`${key}.created`)}</p>
            <Button as={Link} role="link" to={`/activities/${encodeURIComponent(result.activity_id)}`}>{t(`${key}.view_activity`)}</Button>
        </div>}
                {message && <div className="alert alert-danger" role="alert">{message}</div>}
                {!options && !message && <p className="loading">{t(`${key}.loading`)}</p>}
                {options && !result && <>
                    <p>{t(`${key}.balance`, { count: options.ai_generation_credits })}</p>
                    {mode === 'errors' && <>
                            <form onSubmit={generate}>
                                {options.student_username && <div className="alert alert-info">
                                    <p className="mb-1">{t(`${key}.student_context`, { student: options.student_username, activities: selected.map(id => options.activities.find(activity => activity.activity_id === id)?.title || id).join(', ') })}</p>
                                    <Button variant="link" className="p-0" disabled={busy} as={Link} role="link" to="/activities/generate">{t(`${key}.personal_metrics`)}</Button>
                                </div>}
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
                                <p className="fw-semibold" aria-live="polite">{t(`${key}.total`, { count: requiredCredits })}</p>
                                {total > 100 && <p className="text-danger">{t(`${key}.too_many`)}</p>}
                                {requiredCredits > options.ai_generation_credits && <p className="text-danger">{t(`${key}.insufficient`)}</p>}
                                <Button type="submit" disabled={busy || !title.trim() || total < 1 || total > 100 || requiredCredits > options.ai_generation_credits || (datasetMode === 'custom' && (!datasetSql.trim() || !searchPath.trim()))}>
                                    {t(`${key}.${busy ? 'generating' : 'button'}`)}
                                </Button>
                                {progress && <div className="mt-3" role="status" aria-live="polite">
                                    <p>{t(`${key}.progress_${progress.stage}`, progress)}</p>
                                    <ProgressBar animated striped
                                        now={progress.stage === 'saving' ? 100 : progress.stage === 'exercises' ? 100 * (progress.completed + progress.failed) / progress.total : 0}
                                        aria-label={t(`${key}.generating`)} />
                                    <p className="mt-2 mb-1">{t(`${key}.wait`)}</p>
                                </div>}
                                </div>
                            </form>
                    </>}
                    {mode === 'students' && <>
                        <p>{t(`${key}.students_help`)}</p>
                        <div className="row g-4">
                            <section className="col-md-6" aria-labelledby="generation-activities-heading">
                                <h2 className="h5" id="generation-activities-heading">{t(`${key}.source_activities`)}</h2>
                                {options.activities.length === 0 && <p>{t(`${key}.no_activities`)}</p>}
                                {options.activities.map(activity => <div className="form-check" key={activity.activity_id}>
                                    <input className="form-check-input" id={`source-${activity.activity_id}`} type="checkbox" checked={selected.includes(activity.activity_id)} disabled={busy}
                                        onChange={e => toggleActivity(activity.activity_id, e.target.checked)} />
                                    <label className="form-check-label" htmlFor={`source-${activity.activity_id}`}>{activity.title} ({activity.activity_id})</label>
                                </div>)}
                            </section>
                            <section className="col-md-6" aria-labelledby="generation-students-heading" aria-busy={studentsLoading}>
                                <h2 className="h5" id="generation-students-heading">{t(`${key}.students`)}</h2>
                                {!selected.length && <p>{t(`${key}.select_activities`)}</p>}
                                {studentsLoading && <p role="status">{t(`${key}.loading`)}</p>}
                                {students !== null && (students.length
                                    ? <ul>{students.map(student => <li key={student}><Button variant="link" disabled={busy} as={Link} role="link" to={studentPath(student)}>{student}</Button></li>)}</ul>
                                    : <p>{t(`${key}.no_students`)}</p>)}
                            </section>
                        </div>
                    </>}
                </>}
    </div>;
}
