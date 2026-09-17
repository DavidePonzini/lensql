import { useTranslation } from 'react-i18next';

function Privacy() {
    const { t } = useTranslation();
    const sections = [
        'controller', 'project_contact', 'legal_basis', 'purposes', 'data',
        'provision', 'processing', 'retention', 'recipients', 'transfers',
        'rights', 'complaint', 'updates',
    ];

    return (
        <div className="container py-4">
            <h1 className="mb-3">{t('pages.privacy.title')}</h1>
            <p className="text-muted">{t('pages.privacy.updated')}</p>

            <p>{t('pages.privacy.intro')}</p>

            {sections.map((section) => (
                <section key={section}>
                    <h4 className="mt-4">{t(`pages.privacy.${section}_title`)}</h4>
                    <p>{t(`pages.privacy.${section}_body`)}</p>
                </section>
            ))}
        </div>
    );
}

export default Privacy;
