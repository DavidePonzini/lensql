import { useEffect, useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";
import useAuth from "../../hooks/useAuth";

import "./Query.css";

import SqlEditor from "./SqlEditor";
import QueryResult from "./QueryResult";
import ButtonsQuery from "./ButtonsQuery";
import ButtonsDatabase from "./ButtonsDatabase";
import ButtonsExercise from "./ButtonsExercise";
import ButtonAction from "../../components/buttons/ButtonAction";
import { Button } from "react-bootstrap";

function Query({ exerciseId, datasetId, exerciseTitle, exerciseText, attempts, hasSolution, lastQuery }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();

    const SCROLL_GRACE_PERIOD = 500; // milliseconds

    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);
    const [showTopBtn, setShowTopBtn] = useState(false);

    const scheduledScrollRef = useRef(null);
    const resultEndRef = useRef(null);

    async function handleCreateDataset() {
        setIsExecuting(true);
        setResult([]);

        try {
            const stream = await apiRequest('/api/exercises/init-dataset', 'POST', {
                'exercise_id': exerciseId,
            }, { stream: true });

            const reader = stream.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                if (value) {
                    buffer += decoder.decode(value, { stream: true });

                    let lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep last partial line

                    for (let line of lines) {
                        if (line.trim() === '') continue;
                        try {
                            const parsed = JSON.parse(line);
                            setResult(prev => [...prev, parsed]);
                        } catch (e) {
                            console.error('Failed to parse line:', line);
                        }
                    }
                }
            }

            if (buffer.trim() !== '') {
                try {
                    const parsed = JSON.parse(buffer);
                    setResult(prev => [...prev, parsed]);
                } catch (e) {
                    console.error('Failed to parse last buffer:', buffer);
                }
            }

        } catch (error) {
            alert(t('pages.exercises.buttons.exercise.dataset_error'));
            console.error('Streaming error:', error);
        } finally {
            setIsExecuting(false);
        }
    }


    // Show a "Scroll to Top" button when the user scrolls down
    useEffect(() => {
        function onScroll() {
            setShowTopBtn(window.scrollY > 60);
        }

        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    // Scroll to top when the "Scroll to Top" button is clicked
    function scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }


    // Show a confirmation dialog when the user tries to leave the page with unsaved changes
    useEffect(() => {
        function handleBeforeUnload(e) {
            if (sqlText.length > 0) {
                e.preventDefault();
                e.returnValue = ''; // Required for Chrome to show the confirmation dialog
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [sqlText]);

    // Scroll to the bottom of the result list when new results are added
    useEffect(() => {
        function scroll() {
            scheduledScrollRef.current = null;
            if (resultEndRef.current) {
                resultEndRef.current.scrollIntoView({ behavior: 'smooth' });
            }
        }

        if (scheduledScrollRef.current) {
            clearTimeout(scheduledScrollRef.current);
        }

        scheduledScrollRef.current = setTimeout(scroll, SCROLL_GRACE_PERIOD);
    }, [result]);

    return (
        <>
            <div className="row">
                <div className="col">
                    <h2>{exerciseTitle}</h2>
                </div>
                <div className="col text-end">
                    <NavLink to={`/datasets/${datasetId}`} className="btn btn-link mb-3">
                        <i className="fa-solid fa-arrow-left"></i> {t('pages.exercises.query.back_to_dataset')}
                    </NavLink>
                </div>
            </div>

            <p className="exercise-request" style={{ position: 'relative', paddingLeft: '1rem' }}>{exerciseText}</p>

            <ButtonAction
                variant="secondary"
                className="mb-3"
                onClick={handleCreateDataset}
                disabled={isExecuting}
            >
                {t('pages.exercises.query.init_dataset')}
            </ButtonAction>

            <SqlEditor onChange={setSqlText} value={lastQuery || ''} />

            <div className="mt-3 support-buttons">
                <div className="row">
                    <ButtonsQuery
                        exerciseId={exerciseId}
                        isExecuting={isExecuting}
                        setIsExecuting={setIsExecuting}
                        sqlText={sqlText}
                        result={result}
                        setResult={setResult}
                    />
                </div>

                <div className="row">
                    <ButtonsExercise
                        exerciseId={exerciseId}
                        datasetId={datasetId}
                        handleCreateDataset={handleCreateDataset}
                        sqlText={sqlText}
                        attempts={attempts}
                        hasSolution={hasSolution}
                        isExecuting={isExecuting}
                        setIsExecuting={setIsExecuting}
                        setResult={setResult}
                    />
                </div>

                <div className="row">
                    <ButtonsDatabase
                        exerciseId={exerciseId}
                        isExecuting={isExecuting}
                        setIsExecuting={setIsExecuting}
                        setResult={setResult}
                    />
                </div>
            </div >

            <div className="mt-3">
                {
                    result.map((val, index) => (
                        <QueryResult
                            result={val.data}
                            isBuiltin={val.builtin}
                            queryId={val.id}
                            query={val.query}
                            key={val.id ? val.id : `i${index}`}
                            success={val.success}
                            isMessage={val.data_type === 'message'}
                            notices={val.notices}
                            ref={index === result.length - 1 ? resultEndRef : null}
                        />
                    ))
                }
            </div>

            {showTopBtn && (
                <button
                    onClick={scrollToTop}
                    style={{
                        position: 'fixed',
                        bottom: '1.5rem',
                        right: '1.5rem',
                        zIndex: 1030,
                        border: 'none',
                        borderRadius: '50%',
                        width: 48,
                        height: 48,
                        fontSize: '1.25rem',
                        background: '#0d6efd',
                        color: '#fff',
                        boxShadow: '0 2px 6px rgba(0,0,0,.3)',
                        cursor: 'pointer'
                    }}
                    aria-label={t('pages.exercises.query.back_to_top')}
                    title={t('pages.exercises.query.back_to_top')}
                >
                    ↑
                </button>
            )}

        </>
    );
}

export default Query;