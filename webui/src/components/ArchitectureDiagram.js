import { useTranslation } from 'react-i18next';

import diagram from '../res/lensql-architecture.png';

function ArchitectureDiagram() {
    const { t } = useTranslation();

    return (
        <section className="mb-4">
            <h2 className="h4 text-success">{t('pages.about.architectureTitle')}</h2>
            <p>{t('pages.about.architectureIntro')}</p>
            <img
                src={diagram}
                alt={t('pages.about.architectureAlt')}
                className="d-block img-fluid w-100 border rounded"
                width="1526"
                height="754"
                loading="lazy"
            />
        </section>
    );
}

export default ArchitectureDiagram;
