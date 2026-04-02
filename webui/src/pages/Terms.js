import { useTranslation } from 'react-i18next';

function Terms() {
    const { t } = useTranslation();

    return (
        <div className="container py-4">
            <h1 className="mb-3">{t('pages.terms.title')}</h1>
            <p className="text-muted">{t('pages.terms.updated')}</p>

            <h4 className="mt-4">{t('pages.terms.use_title')}</h4>
            <p>{t('pages.terms.use_body')}</p>

            <h4 className="mt-4">{t('pages.terms.account_title')}</h4>
            <p>{t('pages.terms.account_body')}</p>

            <h4 className="mt-4">{t('pages.terms.content_title')}</h4>
            <p>{t('pages.terms.content_body')}</p>

            <h4 className="mt-4">{t('pages.terms.liability_title')}</h4>
            <p>{t('pages.terms.liability_body')}</p>

            <h4 className="mt-4">{t('pages.terms.contact_title')}</h4>
            <p>{t('pages.terms.contact_body')}</p>
        </div>
    );
}

export default Terms;
