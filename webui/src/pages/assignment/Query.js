import { useEffect, useState } from "react";
import { useAuth, RequestSizeError } from "../../hooks/useAuth";

import "./Query.css";

import SqlEditor from "./SqlEditor";
import QueryResult from "./QueryResult";
import ButtonShowDataset from "../../components/ButtonShowDataset";
import ButtonAction from "../../components/ButtonAction";
import ButtonActionDropdown from "../../components/ButtonActionDropdown";

function ButtonCategory({ text, className, iconClassName }) {
    return (
        <div
            className={`col-auto ${className}`}
            style={{
                alignContent: 'center',
                marginBottom: '0.25rem',
                width: 120,
            }}
        >
            <i className={`${iconClassName} mx-1`}></i>
            {text}:
        </div>
    );
}

function Query({ exerciseId, exerciseTitle, exerciseText, datasetName }) {
    const { apiRequest } = useAuth();
    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);

    const buttonShowSearchPathLocked = false;
    const buttonListTablesLocked = false;
    const buttonListAllTablesLocked = false;
    const buttonListSchemasLocked = false;
    const buttonListConstraintsLocked = false;

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
            const stream = await apiRequest('/api/queries/run', 'POST', {
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

    async function handleCheckResult() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/view-expected-result', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleShowSearchPath() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/show-search-path', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListSchemas() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-schemas', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListAllTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-all-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        displayResult(data);
    }

    async function handleListConstraints() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-constraints', 'POST', {
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
            alert('Error when creating dataset. See console for details.\nIf the dataset is very large, you can try manually executing commands in smaller batches.');
            console.error('Streaming error:', error);
        } finally {
            setIsExecuting(false);
        }
    }

    return (
        <>
            <h2 className="exercise-title">{exerciseTitle}</h2>
            <p className="exercise-request" style={{ position: 'relative', paddingLeft: '1rem' }}>{exerciseText}</p>

            <SqlEditor onChange={setSqlText} onSubmit={handleExecute} />

            <div className="mt-3 support-buttons">
                <div className="row">
                    <ButtonCategory
                        text="Query"
                        iconClassName='fas fa-align-left'
                        className="text-primary"
                    />

                    <div className="col">
                        <ButtonAction
                            variant="primary"
                            className="me-1 mb-1"
                            onClick={handleExecute}
                            disabled={isExecuting || sqlText.trim().length === 0}
                        >
                            Execute
                        </ButtonAction>

                        <ButtonAction
                            variant="outline-primary"
                            className="me-1 mb-1"
                            onClick={handleClearOutput}
                            disabled={isExecuting || result.length === 0}
                        >
                            Clear output
                        </ButtonAction>
                    </div>
                </div>

                <div className="row">
                    <ButtonCategory
                        text="Exercise"
                        iconClassName='fas fa-tasks'
                        className="text-info"
                    />

                    <div className="col">
                        <ButtonShowDataset
                            variant="info"
                            className="me-1 mb-1"
                            buttonText="Dataset"
                            datasetName={datasetName}
                            disabled={isExecuting}
                            footerButtons={[
                                {
                                    text: 'Create',
                                    variant: 'primary',
                                    onClick: handleCreateDataset,
                                    autoClose: true,
                                    disabled: isExecuting,
                                },
                            ]}
                        />

                        <ButtonAction
                            variant="warning"
                            className="me-1 mb-1"
                            onClick={handleCheckResult}
                            disabled={isExecuting}
                        >
                            Check Result
                        </ButtonAction>
                    </div>
                </div>

                <div className="row">
                    <ButtonCategory
                        text="Database"
                        iconClassName='fas fa-database'
                        className="text-secondary"
                    />
                    <div className="col">

                        <ButtonAction
                            variant="secondary"
                            className="me-1 mb-1"
                            onClick={handleShowSearchPath}
                            disabled={isExecuting}
                            locked={buttonShowSearchPathLocked}
                        >
                            Show Search Path
                        </ButtonAction>

                        <ButtonActionDropdown
                            title="List Tables"
                            disabled={isExecuting}
                            locked={buttonListTablesLocked && buttonListAllTablesLocked}
                            variant="secondary"
                            className="me-1 mb-1"
                            buttons={[
                                {
                                    label: 'Current Schema',
                                    onClick: handleListTables,
                                    disabled: isExecuting,
                                    locked: buttonListTablesLocked,
                                },
                                {
                                    label: 'All Schemas',
                                    onClick: handleListAllTables,
                                    disabled: isExecuting,
                                    locked: buttonListAllTablesLocked,
                                },
                            ]}
                        />

                        <ButtonAction
                            variant="secondary"
                            className="me-1 mb-1"
                            onClick={handleListSchemas}
                            disabled={isExecuting}
                            locked={buttonListSchemasLocked}
                        >
                            List Schemas
                        </ButtonAction>

                        <ButtonAction
                            variant="secondary"
                            className="me-1 mb-1"
                            onClick={handleListConstraints}
                            disabled={isExecuting}
                            locked={buttonListConstraintsLocked}
                        >
                            List Constraints
                        </ButtonAction>
                    </div>
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