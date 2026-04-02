import { useTranslation } from 'react-i18next';

function Privacy() {
    const { t } = useTranslation();

    return (
        <div className="container py-4">
            <h1 className="mb-3">{t('pages.privacy.title')}</h1>
            <p className="text-muted">{t('pages.privacy.updated')}</p>

            <h4 className="mt-4">{t('pages.privacy.data_title')}</h4>
            <p>{t('pages.privacy.data_body')}</p>

            <h4 className="mt-4">{t('pages.privacy.use_title')}</h4>
            <p>{t('pages.privacy.use_body')}</p>

            <h4 className="mt-4">{t('pages.privacy.disclosure_title')}</h4>
            <p>{t('pages.privacy.disclosure_body')}</p>

            <h4 className="mt-4">{t('pages.privacy.rights_title')}</h4>
            <p>{t('pages.privacy.rights_body')}</p>

            <h4 className="mt-4">{t('pages.privacy.contact_title')}</h4>
            <p>{t('pages.privacy.contact_body')}</p>
        </div>
    );
}

export default Privacy;
