import { useTranslation } from 'react-i18next';

function Cookies() {
    const { t } = useTranslation();

    return (
        <div className="container py-4">
            <h1 className="mb-3">{t('pages.cookies.title')}</h1>
            <p className="text-muted">{t('pages.cookies.updated')}</p>

            <h4 className="mt-4">{t('pages.cookies.what_title')}</h4>
            <p>{t('pages.cookies.what_body')}</p>

            <h4 className="mt-4">{t('pages.cookies.how_title')}</h4>
            <p>{t('pages.cookies.how_body')}</p>

            <h4 className="mt-4">{t('pages.cookies.manage_title')}</h4>
            <p>{t('pages.cookies.manage_body')}</p>

            <h4 className="mt-4">{t('pages.cookies.necessary_title')}</h4>
            <p>{t('pages.cookies.necessary_body')}</p>

            <h4 className="mt-4">{t('pages.cookies.research_title')}</h4>
            <p>{t('pages.cookies.research_body')}</p>
        </div>
    );
}

export default Cookies;
