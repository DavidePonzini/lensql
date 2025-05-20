import { useEffect, useState } from "react";
import { useAuth, RequestSizeError } from "../hooks/useAuth";

import "../styles/Query.css";

import SqlEditor from "./SqlEditor";
import QueryResult from "./QueryResult";
import ButtonShowDataset from "./ButtonShowDataset";

function Query({ exerciseId, exerciseTitle, exerciseText, datasetId }) {
    const { apiRequest } = useAuth();
    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);

    function displayResult(data) {
        setResult(data);
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
        if (!sqlText.trim()) return;

        setIsExecuting(true);
        setResult([]);

        try {
            const stream = await apiRequest('/api/run-query', 'POST', {
                'query': sqlText,
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
            if (error instanceof RequestSizeError) {
                alert(`Query too large. Please try to split it into smaller parts. You need to remove at least ${error.size - error.maxSize} characters.`);
            } else {
                alert(error);
                console.error('Streaming error:', error);
            }
        } finally {
            setIsExecuting(false);
        }
    }


    async function handleShowSearchPath() {
        setIsExecuting(true);

        const data = await apiRequest('/api/show-search-path', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListSchemas() {
        setIsExecuting(true);

        const data = await apiRequest('/api/list-schemas', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/list-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListAllTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/list-all-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListConstraints() {
        setIsExecuting(true);

        const data = await apiRequest('/api/list-constraints', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    function handleClearOutput() {
        setResult([]);
    }

    async function handleCreateDataset() {
        setIsExecuting(true);
        setResult([]);

        try {
            const stream = await apiRequest('/api/create-dataset', 'POST', {
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
            alert('Error when creating dataset. See console for details.\nIf the dataset is very large, you can try manually executing commands in smaller batches.');
            console.error('Streaming error:', error);
        } finally {
            setIsExecuting(false);
        }
    }

    return (
        <>
            <h2 className="exercise-title">{exerciseTitle}</h2>
            <p className="exercise-request">{exerciseText}</p>

            <div className="mb-3" style={{ justifySelf: 'end' }}>
                <ButtonShowDataset
                    className="btn btn-secondary me-1"
                    buttonText="View Dataset"
                    datasetId={datasetId}
                    footerButtons={[
                        {
                            text: 'Create',
                            variant: 'primary',
                            onClick: handleCreateDataset,
                            autoClose: true,
                        },
                    ]}
                />
            </div>

            <SqlEditor onChange={setSqlText} onSubmit={handleExecute} />

            <div className="mt-3 support-buttons">
                <button
                    className="btn btn-primary me-1"
                    disabled={isExecuting || sqlText.trim().length === 0}
                    onClick={handleExecute}
                >
                    Execute
                </button>

                <button
                    className="btn btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleShowSearchPath}
                >
                    Show Search Path
                </button>

                <button
                    className="btn btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleListSchemas}
                >
                    List Schemas
                </button>

                <div className="btn-group me-1" role="group">
                    <button
                        className="btn btn-secondary dropdown-toggle"
                        type="button"
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                        disabled={isExecuting}
                    >
                        List Tables
                    </button>
                    <ul className="dropdown-menu">
                        <li>
                            <button
                                className="dropdown-item"
                                onClick={handleListTables}
                            >
                                Current Schema
                            </button>
                        </li>
                        <li>
                            <button
                                className="dropdown-item"
                                onClick={handleListAllTables}
                            >
                                All Schemas
                            </button>
                        </li>
                    </ul>
                </div>

                <button
                    className="btn btn-secondary me-1"
                    disabled={isExecuting}
                    onClick={handleListConstraints}
                >
                    List Constraints
                </button>

                <button
                    className="btn btn-primary"
                    disabled={isExecuting}
                    onClick={handleClearOutput}
                >
                    Clear output
                </button>
            </div>

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
                            isMessage={val.type === 'message'}
                            notices={val.notices}
                        />
                    ))
                }
            </div>
        </>
    );
}

export default Query;