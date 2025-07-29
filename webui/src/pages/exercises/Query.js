import { useEffect, useState, useRef } from "react";
import { useTranslation } from "react-i18next";

import "./Query.css";

import SqlEditor from "./SqlEditor";
import QueryResult from "./QueryResult";
import ButtonsQuery from "./ButtonsQuery";
import ButtonsDatabase from "./ButtonsDatabase";
import ButtonsExercise from "./ButtonsExercise";

function Query({ exerciseId, classId, exerciseTitle, exerciseText, attempts, hasSolution }) {
    const { t } = useTranslation();

    const SCROLL_GRACE_PERIOD = 500; // milliseconds

    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);
    const [showTopBtn, setShowTopBtn] = useState(false);

    const scheduledScrollRef = useRef(null);
    const resultEndRef = useRef(null);

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
            <h2 className="exercise-title">{exerciseTitle}</h2>
            <p className="exercise-request" style={{ position: 'relative', paddingLeft: '1rem' }}>{exerciseText}</p>

            <SqlEditor onChange={setSqlText} />

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
                        classId={classId}
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