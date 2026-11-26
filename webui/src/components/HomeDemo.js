import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Modal from 'react-bootstrap/Modal';

import ButtonAction from './buttons/ButtonAction';
import LearningStatsErrors from './learningStats/LearningStatsErrors';
import MessageBox from '../pages/exercises/MessageBox';

import './learningStats/LearningStats.css';
import '../pages/exercises/QueryResult.css';
import './HomeDemo.css';

const query = `SELECT category, category
FROM books
WHERE publisher LIKE 'Northstar'
  AND price >= 10 AND price >= 5
ORDER BY category;`;

const categories = ['Fiction', 'Fiction', 'History'];
const errors = [40, 51, 88, 72];
const sampleStats = {
    errors: [
        { error_id: 35, category: 'SYN', count: 5, query_goal: 'FOCUSED' },
        { error_id: 17, category: 'SYN', count: 3, query_goal: 'FOCUSED' },
        { error_id: 14, category: 'SYN', count: 2, query_goal: 'FOCUSED' },
        { error_id: 40, category: 'SEM', count: 10, query_goal: 'FOCUSED' },
        { error_id: 51, category: 'SEM', count: 6, query_goal: 'FOCUSED' },
        { error_id: 88, category: 'COM', count: 8, query_goal: 'FOCUSED' },
        { error_id: 72, category: 'LOG', count: 16, query_goal: 'FOCUSED' },
    ],
    timeline: [
        { date: '2026-03-10', query_goal: 'FOCUSED', query_count: 5, errors: { SYN: 4, SEM: 4, COM: 1, LOG: 2 } },
        { date: '2026-03-11', query_goal: 'FOCUSED', query_count: 7, errors: { SYN: 3, SEM: 2, COM: 2, LOG: 4 } },
        { date: '2026-03-12', query_goal: 'FOCUSED', query_count: 6, errors: { SYN: 2, SEM: 5, COM: 1, LOG: 2 } },
        { date: '2026-03-13', query_goal: 'FOCUSED', query_count: 8, errors: { SYN: 1, SEM: 2, COM: 2, LOG: 3 } },
        { date: '2026-03-14', query_goal: 'FOCUSED', query_count: 10, errors: { SEM: 2, COM: 1, LOG: 3 } },
        { date: '2026-03-15', query_goal: 'FOCUSED', query_count: 12, errors: { SEM: 1, COM: 1, LOG: 2 } },
    ],
};

function HomeDemo() {
    const { t } = useTranslation();
    const [step, setStep] = useState(0);
    const [showStats, setShowStats] = useState(false);

    return (
        <>
            <section className="col-lg-6" aria-labelledby="home-demo-title">
                <div className="card shadow-sm">
                    <div className="card-body p-3 p-md-4">
                        <h2 id="home-demo-title" className="h4 mb-2">{t('pages.home.demo.title')}</h2>
                        <p>{t('pages.home.demo.task')}</p>
                        <pre className="bg-dark text-white rounded p-3"><code>{query}</code></pre>
                        <ButtonAction variant="primary" onClick={() => setStep(1)}>
                            {t('pages.home.demo.run')}
                        </ButtonAction>

                        <div aria-live="polite">
                            {step >= 1 && (
                                <div className="home-demo-reveal">
                                    <div className="query-result alert alert-primary mb-0">
                                        <h3 className="h6">{t('pages.home.demo.result')}</h3>
                                        <div className="table-responsive">
                                            <table className="table table-bordered table-hover">
                                                <thead>
                                                    <tr><th scope="col">category</th><th scope="col">category</th></tr>
                                                </thead>
                                                <tbody>
                                                    {categories.map((category, index) => (
                                                        <tr key={index}>
                                                            <td>{category}</td><td>{category}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                        <ButtonAction variant="warning" onClick={() => setStep(current => Math.max(current, 2))}>
                                            {t('pages.exercises.chat.buttons.detect_errors')}
                                        </ButtonAction>

                                        {step >= 2 && (
                                            <div className="home-demo-reveal">
                                                <div className="home-demo-feedback">
                                                    <MessageBox assistant>
                                                        <ul className="mb-0 ps-3">
                                                            {errors.map(id => (
                                                                <li key={id}>
                                                                    <strong>{t(`errors.errors.${id}.name`)}</strong>
                                                                    <div>{t(`pages.home.demo.errors.${id}`)}</div>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </MessageBox>
                                                    <ButtonAction variant="outline-primary" className="mt-3" onClick={() => setShowStats(true)}>
                                                        {t('pages.home.demo.stats')}
                                                    </ButtonAction>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            <Modal
                show={showStats}
                onHide={() => setShowStats(false)}
                size="xl"
                scrollable
                aria-labelledby="home-demo-stats-title"
            >
                <Modal.Header closeButton closeLabel={t('components.buttons.modal.close')}>
                    <Modal.Title as="h2" id="home-demo-stats-title">
                        {t('pages.home.demo.stats')}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p>{t('pages.home.demo.statsIntro')}</p>
                    <LearningStatsErrors sampleData={sampleStats} />
                </Modal.Body>
            </Modal>
        </>
    );
}

export default HomeDemo;
