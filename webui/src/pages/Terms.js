import { useTranslation } from 'react-i18next';

function Terms() {
    const { t } = useTranslation();
    const sections = [
        'provider',
        'use',
        'account',
        'content',
        'availability',
        'law',
        'contact',
    ];

    return (
        <div className="container py-4">
            <h1 className="mb-3">{t('pages.terms.title')}</h1>
            <p className="text-muted">{t('pages.terms.updated')}</p>

            {sections.map((section) => (
                <section key={section}>
                    <h4 className="mt-4">{t(`pages.terms.${section}_title`)}</h4>
                    <p>{t(`pages.terms.${section}_body`)}</p>
                </section>
            ))}
        </div>
    );
}

export default Terms;
