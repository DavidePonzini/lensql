import { useTranslation } from 'react-i18next';

export default function DatasetTips() {
    const { t } = useTranslation();
    const tips = t('pages.activities.activity_mask.tips', { returnObjects: true });
    return <div>
        <b>{t('pages.activities.activity_mask.tips_title')}</b>
        <ul>{tips.map((tip, index) => <li key={index} dangerouslySetInnerHTML={{ __html: tip }} />)}</ul>
    </div>;
}
