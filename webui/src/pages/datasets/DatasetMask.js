import { useTranslation } from 'react-i18next';

function DatasetMask({ title, setTitle, dataset, setDataset }) {
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
                />
            </div>
            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.dataset_mask.dataset_label')}</label>
                <textarea
                    className="form-control monospace"
                    rows="10"
                    defaultValue={dataset}
                    onInput={(e) => setDataset(e.target.value)}
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

export default ClassMask;
