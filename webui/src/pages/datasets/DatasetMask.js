import { useTranslation } from 'react-i18next';

function DatasetMask({ title, setTitle, description, setDescription, dataset, setDataset }) {
    const { t } = useTranslation();

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
        </>
    );
}

export default DatasetMask;
