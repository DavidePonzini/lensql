import { useTranslation } from 'react-i18next';
import useUserInfo from '../../hooks/useUserInfo';

function DatasetMask({
    title,
    setTitle,
    description,
    setDescription,
    dataset,
    setDataset,
    searchPath,
    setSearchPath,
    dbms,
    setDbms,
    activityStartTs,
    setActivityStartTs,
    activityEndTs,
    setActivityEndTs,
}) {
    const { t } = useTranslation();
    const { userInfo } = useUserInfo();
    const isTeacher = userInfo?.isTeacher || false;

    if (dbms == '') {
        setDbms('postgres');
    }

    const tips = t('pages.datasets.dataset_mask.tips', { returnObjects: true });

    return (
        <>
            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.title_label')}</label>
                <input
                    type="text"
                    className="form-control"
                    defaultValue={title}
                    onInput={(e) => setTitle(e.target.value)}
                    placeholder={t('pages.datasets.dataset_mask.title_placeholder')}
                />
            </div>
            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.description_label')}</label>
                <input
                    type="text"
                    className="form-control"
                    defaultValue={description}
                    onInput={(e) => setDescription(e.target.value)}
                    placeholder={t('pages.datasets.dataset_mask.description_placeholder')}
                />
            </div>
            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.dataset_label')}</label>
                <textarea
                    className="form-control monospace"
                    rows="11"
                    defaultValue={dataset}
                    onInput={(e) => setDataset(e.target.value)}
                    placeholder={t('pages.datasets.dataset_mask.dataset_str_placeholder')}
                />
                <div>
                    <b>{t('pages.datasets.dataset_mask.tips_title')}</b>
                    <ul>
                        {tips.map((tip, idx) => (
                            <li key={idx} dangerouslySetInnerHTML={{ __html: tip }} />
                        ))}
                    </ul>
                </div>
            </div>

            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.search_path_label')}</label>
                <input
                    type="text"
                    className="form-control"
                    defaultValue={searchPath}
                    onInput={(e) => {
                        setSearchPath(e.target.value);
                    }}
                    placeholder='public'
                />
            </div>

            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.dbms_label')}</label>
                <select
                    className="form-select"
                    value={dbms}
                    onChange={(e) => setDbms(e.target.value)}
                >
                    <option value="postgres">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option disabled value="sqlite">SQLite</option>
                    <option disabled value="sqlserver">SQL Server</option>
                    <option disabled value="oracle">Oracle</option>
                </select>
            </div>

            {isTeacher && (
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <label className="form-label">{t('pages.datasets.dataset_mask.activity_start_label')}</label>
                        <input
                            type="datetime-local"
                            className="form-control"
                            value={activityStartTs}
                            onChange={(e) => setActivityStartTs(e.target.value)}
                        />
                    </div>
                    <div className="col-md-6 mb-3">
                        <label className="form-label">{t('pages.datasets.dataset_mask.activity_end_label')}</label>
                        <input
                            type="datetime-local"
                            className="form-control"
                            value={activityEndTs}
                            onChange={(e) => setActivityEndTs(e.target.value)}
                        />
                    </div>
                </div>
            )}
        </>
    );
}

export default DatasetMask;
