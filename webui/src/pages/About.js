import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import ArchitectureDiagram from '../components/ArchitectureDiagram';
import useAuth from '../hooks/useAuth';

const papers = [
    { file: 'SEBD2025.pdf', translationKey: 'paper1' },
    { file: 'ADBIS2025.pdf', translationKey: 'paper2' },
    { file: 'DataEd2026.pdf', translationKey: 'paper3' },
    { file: 'ADBIS2026.pdf', translationKey: 'paper4' },
];

function About() {
    const { isLoggedIn } = useAuth();
    const { t } = useTranslation();

    return (
        <div className="container-md py-4">
            <header className="mb-4">
                <h1 className="text-primary">{t('pages.about.title')}</h1>
                <p className="lead mb-0">{t('pages.about.intro')}</p>
            </header>

            <div className="row g-3 mb-4">
                {['students', 'teachers'].map(role => (
                    <section className="col-md-6" key={role}>
                        <div className="card h-100">
                          <div className="card-body p-4">
                                <h2 className="h4 text-success">{t(`pages.about.${role}.title`)}</h2>
                                <p>{t(`pages.about.${role}.practice`)}</p>
                                <p className="mb-0">{t(`pages.about.${role}.progress`)}</p>
                            </div>
                        </div>
                    </section>
                ))}
            </div>

            <ArchitectureDiagram />

            <section className="mb-4">
                <h2 className="h4 text-success">{t('pages.about.moreTitle')}</h2>
                <p>{t('pages.about.moreIntro')}</p>
                <ul className="list-group">
                    {papers.map(({ file, translationKey }) => {
                        const title = t(`pages.about.${translationKey}`);

                        return (
                            <li key={file} className="list-group-item py-3 d-flex align-items-start justify-content-between gap-3">
                                <div>
                                    <h3 className="h6 fw-semibold mb-1">{title}</h3>
                                    <p className="mb-0">{t(`pages.about.${translationKey}Desc`)}</p>
                                </div>
                                <a
                                    href={`/files/${file}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="link-body-emphasis d-flex flex-column align-items-center gap-1 text-decoration-none flex-shrink-0"
                                    aria-label={t('pages.about.viewPaper', { title })}
                                >
                                    <i className="bi bi-file-earmark-pdf text-danger fs-4 lh-1" aria-hidden="true" />
                                    <small>{t('pages.about.viewPdf')}</small>
                                </a>
                            </li>
                        );
                    })}
                </ul>
            </section>

            <div className="d-flex flex-wrap gap-2">
                <Link className="btn btn-primary" to={isLoggedIn ? '/activities' : '/register'}>
                    {t(isLoggedIn ? 'pages.home.activities' : 'pages.home.register')}
                </Link>
                <Link className="btn btn-outline-secondary" to="/howto">
                    {t('pages.home.tutorial')}
                </Link>
            </div>
        </div>
    );
}

export default About;
