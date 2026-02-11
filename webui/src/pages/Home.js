import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import useAuth from '../hooks/useAuth';

import Parallax from '../components/Parallax';
import Tutorial from '../components/Tutorial';

import bg from '../res/database.jpg';


function Home() {
    const { isLoggedIn } = useAuth();
    const { t } = useTranslation();

    return (
        <Parallax image={bg}>
            <div className="container pt-5 px-0 bg-light">

                {/* 1. Hero Section */}
                <section className="text-center p-3">
                    <h1 className="display-4 fw-bold text-primary">
                        {t('pages.home.hero.title')}
                    </h1>
                    <p className="lead text-secondary">
                        {t('pages.home.hero.subtitle')}
                    </p>
                    <p className="fs-5">
                        {t('pages.home.hero.description')}
                    </p>
                    <div className="mt-4">
                        <Link to={isLoggedIn ? "/datasets" : "/register"} className="btn btn-primary me-3">
                            {t('pages.home.hero.cta_register')}
                        </Link>
                        <Link to="/howto" className="btn btn-outline-secondary me-3">
                            {t('pages.home.hero.cta_howto')}
                        </Link>
                        <Link to="/about" className="btn btn-outline-success">
                            {t('pages.home.hero.cta_about')}
                        </Link>
                    </div>
                </section>

                {/* 2. What is LensQL */}
                <section className="text-center p-3 bg-white">
                    <h2 className="text-success mb-3">{t('pages.home.what_is.title')}</h2>
                    <p className="fs-4">{t('pages.home.what_is.subtitle')}</p>
                    <div className="row justify-content-center mt-4">
                        <div className="col-md-8 text-start">
                            <ul className="list-unstyled fs-5">
                                {['ai_tutor', 'error_pedagogy', 'personalization'].map(key => (
                                    <li key={key} dangerouslySetInnerHTML={{ __html: t(`pages.home.what_is.features.${key}`) }} />
                                ))}
                            </ul>
                        </div>
                        <blockquote className="blockquote mt-4 fst-italic text-muted">
                            {t('pages.home.what_is.quote')}
                        </blockquote>
                    </div>
                </section>

                {/* 3. How LensQL Works */}
                <section id="how-it-works" className="p-3">
                    <h2 className="text-success text-center mb-4">{t('pages.home.how_it_works.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <ol className="list-group list-group-numbered fs-5">
                                {t('pages.home.how_it_works.steps', { returnObjects: true }).map((step, i) => (
                                    <li className="list-group-item" key={i}>{step}</li>
                                ))}
                            </ol>
                            <div className="text-center mt-4">
                                <Link to="/about" className="btn btn-outline-secondary">
                                    {t('pages.home.how_it_works.cta_research')}
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 4. Meet Lens */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">{t('pages.home.meet_lens.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <p className="fs-5">{t('pages.home.meet_lens.description')}</p>
                            <div className="mt-4">
                                <ul className="list-unstyled fs-5">
                                    {['explain_errors', 'locate_mistakes', 'show_examples', 'describe_query', 'suggest_after_reflection'].map(key => (
                                        <li key={key} dangerouslySetInnerHTML={{ __html: t(`pages.home.meet_lens.features.${key}`) }} />
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 5. Why Learn From Errors? */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">{t('pages.home.why_errors.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <div className="row">
                                {['students', 'teachers'].map(role => (
                                    <div className="col-md-6 mb-4" key={role}>
                                        <h5 className="text-primary">{t(`pages.home.why_errors.${role}.title`)}</h5>
                                        <ul className="list-unstyled fs-5">
                                            {t(`pages.home.why_errors.${role}.items`, { returnObjects: true }).map((item, i) => (
                                                <li key={i} dangerouslySetInnerHTML={{ __html: item }} />
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* 6. Gamification */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">{t('pages.home.gamification.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <p className="fs-5">{t('pages.home.gamification.description')}</p>

                            {['xp', 'coins'].map(section => (
                                <div key={section}>
                                    <h4 className="mt-4 text-primary">{t(`pages.home.gamification.${section}.title`)}</h4>
                                    <p className="fs-5">{t(`pages.home.gamification.${section}.description`)}</p>
                                    <blockquote className="blockquote text-muted fst-italic">
                                        {t(`pages.home.gamification.${section}.quote`)}
                                    </blockquote>
                                </div>
                            ))}

                            <h5 className="mt-4 text-success">{t('pages.home.gamification.why.title')}</h5>
                            <ul className="list-unstyled fs-5">
                                {t('pages.home.gamification.why.items', { returnObjects: true }).map((item, i) => (
                                    <li key={i} dangerouslySetInnerHTML={{ __html: item }} />
                                ))}
                            </ul>
                        </div>
                    </div>
                </section>

                {/* 7. Dashboard */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">{t('pages.home.dashboard.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <div className="row">
                                {['students', 'teachers'].map(role => (
                                    <div className="col-md-6 mb-4" key={role}>
                                        <h5 className="text-primary">{t(`pages.home.dashboard.${role}.title`)}</h5>
                                        <ul className="list-unstyled fs-5">
                                            {t(`pages.home.dashboard.${role}.items`, { returnObjects: true }).map((item, i) => (
                                                <li key={i}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* 8. Demo */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">{t('pages.home.demo.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-8 text-center">
                            <p className="fs-5">{t('pages.home.demo.description')}</p>

                            <Tutorial />
                        </div>
                    </div>
                </section>

                {/* 9. Community */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">{t('pages.home.community.title')}</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-8">
                            <p className="fs-5 text-center mb-4" dangerouslySetInnerHTML={{ __html: t('pages.home.community.description') }} />
                            <div className="row">
                                {['teachers', 'students'].map(role => (
                                    <div className="col-md-6 mb-4" key={role}>
                                        <h5 className="text-primary">{t(`pages.home.community.${role}.title`)}</h5>
                                        <ul className="list-unstyled fs-5">
                                            {t(`pages.home.community.${role}.items`, { returnObjects: true }).map((item, i) => (
                                                <li key={i}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* 10. CTA */}
                <section className="text-center p-3 pb-5 bg-white border-top">
                    <h2 className="mb-3">{t('pages.home.cta.title')}</h2>
                    <div className="d-flex justify-content-center gap-3 mt-4">
                        <Link to="/register" className="btn btn-lg btn-primary">
                            {t('pages.home.cta.register')}
                        </Link>
                        <Link to="/howto" className="btn btn-lg btn-outline-secondary">
                            {t('pages.home.cta.howto')}
                        </Link>
                        <Link to="/about" className="btn btn-lg btn-outline-success">
                            {t('pages.home.cta.about')}
                        </Link>
                    </div>
                </section>
            </div>
        </Parallax>
    );
}

export default Home;
