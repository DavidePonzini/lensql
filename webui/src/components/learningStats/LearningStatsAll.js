import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Tab, Tabs } from 'react-bootstrap';

import LearningStatsQueries from './LearningStatsQueries';
import LearningStatsMessages from './LearningStatsMessages';
import LearningStatsErrors from './LearningStatsErrors';
import useAuth from '../../hooks/useAuth';
import ObservedOnce from '../ObservedOnce';
import './LearningStats.css';

const endpoints = { execution: 'queries', errors: 'errors', assistance: 'messages' };

function LearningStatsAll({ activityId = null, exerciseId = null, isTeacher = false, requestedTab, onTabChange }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const tabsId = useId();
    const started = useRef(new Set());
    const initialTab = requestedTab ?? 'execution';
    const [view, setView] = useState({ active: initialTab, requested: initialTab, results: {} });
    const key = 'components.learningStats.learning';
    const sections = [
        { id: 'execution', style: 'queries', heading: isTeacher ? 'queries_teacher' : 'queries_student', Stats: LearningStatsQueries },
        { id: 'errors', style: 'errors', heading: 'errors', Stats: LearningStatsErrors },
        { id: 'assistance', style: 'messages', heading: 'messages', Stats: LearningStatsMessages },
    ];

    const loadTab = useCallback(async id => {
        if (started.current.has(id)) return;
        started.current.add(id);
        const params = new URLSearchParams({
            activity_id: activityId || '',
            exercise_id: exerciseId || '',
            is_teacher: isTeacher ? '1' : '0',
        });
        let result;
        try {
            const response = await apiRequest(`/api/users/stats/${endpoints[id]}?${params}`, 'GET');
            result = { data: response.data };
        } catch {
            result = { failed: true };
        }

        setView(current => ({
            ...current,
            active: current.requested === id ? id : current.active,
            results: { ...current.results, [id]: result },
        }));
    }, [activityId, apiRequest, exerciseId, isTeacher]);

    const selectTab = useCallback(id => {
        if (!Object.hasOwn(endpoints, id)) return;
        setView(current => ({
            ...current,
            requested: id,
            active: current.results[id] ? id : current.active,
        }));
        loadTab(id);
    }, [loadTab]);

    useEffect(() => {
        if (requestedTab) selectTab(requestedTab);
    }, [requestedTab, selectTab]);

    return (
        <ObservedOnce onFirstVisible={() => loadTab(initialTab)}>
            <div className="learning-stats-tabs my-4">
                <Tabs
                    activeKey={view.active}
                    id={tabsId}
                    mountOnEnter
                    transition={false}
                    onSelect={onTabChange ?? selectTab}
                >
                    {sections.map(({ id, style, heading, Stats }) => {
                        const result = view.results[id];
                        const loading = !result && (started.current.has(id) || view.requested === id);
                        return (
                            <Tab
                                eventKey={id}
                                key={id}
                                title={
                                    <>
                                        {t(`${key}.tabs.${id}`)}
                                        <span
                                            className={`spinner-border spinner-border-sm ms-2${loading ? '' : ' invisible'}`}
                                            aria-hidden="true"
                                        />
                                        {loading && <span className="visually-hidden"> {t(`${key}.loading`)}</span>}
                                    </>
                                }
                                tabClassName={`learning-stats-section--${style}`}
                                className={`learning-stats-tab-pane learning-stats-section--${style}`}
                            >
                                <div className="learning-stats-section__body">
                                    <div className="learning-stats-section__header">
                                        <h2 className="learning-stats-section__title">{t(`${key}.${heading}`)}</h2>
                                    </div>
                                    {!result ? (
                                        <div className="learning-stats-loading" aria-busy="true" />
                                    ) : result.failed ? (
                                        <p role="alert">{t(`${key}.loadError`)}</p>
                                    ) : <Stats data={result.data} isTeacher={isTeacher} />}
                                </div>
                            </Tab>
                        );
                    })}
                </Tabs>
            </div>
        </ObservedOnce>
    );
}

export default LearningStatsAll;
