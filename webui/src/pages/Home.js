import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import HomeDemo from '../components/HomeDemo';
import useAuth from '../hooks/useAuth';

function Home() {
    const { isLoggedIn } = useAuth();
    const { t } = useTranslation();

    return (
        <div className="container py-4 py-lg-5">
            <div className="row align-items-start justify-content-between g-4 g-lg-5">
                <section className="col-lg-5">
                    <h1 className="display-5 fw-bold text-primary">{t('pages.home.title')}</h1>
                    <p className="lead mb-4">{t('pages.home.description')}</p>
                    <div className="d-flex flex-wrap gap-2">
                        <Link to={isLoggedIn ? '/activities' : '/register'} className="btn btn-primary">
                            {t(isLoggedIn ? 'pages.home.activities' : 'pages.home.register')}
                        </Link>
                        <Link to="/howto" className="btn btn-outline-secondary">
                            {t('pages.home.tutorial')}
                        </Link>
                        <Link to="/error-taxonomy" className="btn btn-outline-secondary">
                            {t('pages.home.exploreErrors')}
                        </Link>
                    </div>
                    <Link to="/about" className="d-inline-block mt-3">{t('pages.home.about')}</Link>
                </section>

                <HomeDemo />
            </div>
        </div>
    );
}

export default Home;
