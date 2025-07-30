import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

function About() {
    const { t } = useTranslation();

    return (
        <div className="container-md">
            <h1 className="text-center text-primary mb-4">{t('pages.about.title')}</h1>

            <p className="fs-5">{t('pages.about.p1')}</p>
            <p className="fs-5">{t('pages.about.p2')}</p>
            <p className="fs-5">{t('pages.about.p3')}</p>

            <h5 className="mt-5 text-success">{t('pages.about.moreTitle')}</h5>
            <p className="fs-5 mb-1">{t('pages.about.moreIntro')}</p>

            <ul className="fs-6 ps-3">
                <li className="mb-1">
                    <a
                        href="/files/SEBD2025.pdf"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-primary text-decoration-none"
                    >
                        <em>{t('pages.about.paper1')}</em>
                    </a>{" "}
                    — {t('pages.about.paper1Desc')}
                </li>
                <li>
                    <a
                        href="/files/ADBIS2025.pdf"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-primary text-decoration-none"
                    >
                        <em>{t('pages.about.paper2')}</em>
                    </a>{" "}
                    — {t('pages.about.paper2Desc')}
                </li>
            </ul>

            <div className="mt-4 text-center">
                <Link className="btn btn-success" to="/register" role="button">{t('pages.about.cta')}</Link>
            </div>
        </div>
    );
}

export default About;
