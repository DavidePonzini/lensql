import { useEffect, useState } from "react";
import useToken from "../hooks/useToken";

import "../styles/Query.css";

import SqlEditor from "./SqlEditor";
import Button from "./Button";
import QueryResult from "./QueryResult";

function Query({ exerciseId, exerciseTitle, exerciseText }) {
    const [token] = useToken();
    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);

    function displayResult(data) {
        setResult(data);

        console.log(data);
    }

    // Show a confirmation dialog when the user tries to leave the page with unsaved changes
    useEffect(() => {
        const handleBeforeUnload = (e) => {
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


    async function handleExecute() {
        if (!sqlText.trim())
            return;

        const query = sqlText;

        setIsExecuting(true);
        try {
            const response = await fetch(`/api/run-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query': query,
                    'exercise_id': exerciseId,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error}`);
        } finally {
            setIsExecuting(false);
        }
    };

    async function handleShowSearchPath() {
        setIsExecuting(true);

        try {
            const response = await fetch(`/api/show-search-path`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'exercise_id': exerciseId,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error}`);
        } finally {
            setIsExecuting(false);
        }
    }

    async function handleListSchemas() {
        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-schemas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'exercise_id': exerciseId,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error}`);
        } finally {
            setIsExecuting(false);
        }
    }

    async function handleListTables() {
        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-tables`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'exercise_id': exerciseId,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error}`);
        } finally {
            setIsExecuting(false);
        }
    }

    async function handleListConstraints() {
        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-constraints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'exercise_id': exerciseId
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            console.error(error);
            alert(`Error: ${error}`);
        } finally {
            setIsExecuting(false);
        }
    }

    function handleClearOutput() {
        setResult([]);
    }

    return (
        <>
            <h2 className="exercise-title">{exerciseTitle}</h2>
            <p className="exercise-request">{exerciseText}</p>

            <SqlEditor onChange={setSqlText} onSubmit={handleExecute} />

            <div className="mt-3 support-buttons">
                <Button
                    className="btn-primary me-1"
                    disabled={isExecuting || sqlText.trim().length === 0}
                    onClick={handleExecute}
                >
                    Execute
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleShowSearchPath}
                >
                    Show Search Path
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleListSchemas}
                >
                    List Schemas
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleListTables}
                >
                    List Tables
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleListConstraints}
                >
                    List Constraints
                </Button>

                <Button
                    className="btn-primary"
                    disabled={isExecuting}
                    onClick={handleClearOutput}
                >
                    Clear output
                </Button>
            </div>

            <div className="mt-3">
                {
                    result.map((val, index) => (
                        <QueryResult
                            result={val.data}
                            isBuiltin={val.builtin}
                            queryId={val.id}
                            query={val.query}
                            success={val.success}
                            isMessage={val.type === 'message'}
                        />
                    ))
                }
            </div>
        </>
    );
}

export default Query;