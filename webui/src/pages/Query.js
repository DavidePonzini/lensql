import { useState } from "react";
import useToken from "../hooks/useToken";

import SqlEditor from "../components/SqlEditor";
import Button from "../components/Button";
import QueryResult from "../components/QueryResult";

function Query({ exerciseId, exerciseText }) {
    const [sqlText, setSqlText] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const [result, setResult] = useState([]);
    const [token, setToken] = useToken();

    const displayResult = (data) => {
        setResult(data);

        console.log(data);
    }

    const handleExecute = async () => {
        if (!sqlText.trim())
            return;

        const username = token.username;
        const query = sqlText;

        setIsExecuting(true);
        try {
            const response = await fetch(`/api/run-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'username': username,
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

    const handleShowSearchPath = async () => {
        const username = token.username;

        setIsExecuting(true);

        try {
            const response = await fetch(`/api/show-search-path`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'username': username,
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

    const handleListSchemas = async () => {
        const username = token.username;

        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-schemas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'username': username,
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

    const handleListTables = async () => {
        const username = token.username;

        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-tables`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'username': username,
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

    const handleListConstraints = async () => {
        const username = token.username;

        setIsExecuting(true);

        try {
            const response = await fetch(`/api/list-constraints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'username': username,
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

    const handleClearOutput = () => {
        setResult([]);
    }

    return (
        <>
            <p className="lead">#{} {exerciseText}</p>

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