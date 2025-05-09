import { useState } from "react";
import useToken from "../hooks/useToken";

import '../styles/Query.css';

import SqlEditor from "../components/SqlEditor";
import Button from "../components/Button";
import QueryResult from "../components/QueryResult";

function Query() {
    const [sqlText, setSqlText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState([]);
    const [token, setToken] = useToken();

    const displayResult = (data) => {
        setResult(data);
        if (!data)
            return;

        console.log(data);
    }

    const handleExecute = async () => {
        if (!sqlText.trim())
            return;

        const username = token.username;
        const query = sqlText;

        setIsLoading(true);
        try {
            const response = await fetch(`/api/run-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    query,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleShowSearchPath = async () => {
        const username = token.username;

        setIsLoading(true);

        try {
            const response = await fetch(`/api/show-search-path`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    }

    const handleListSchemas = async () => {
        const username = token.username;

        setIsLoading(true);

        try {
            const response = await fetch(`/api/list-schemas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    }

    const handleListTables = async () => {
        const username = token.username;

        setIsLoading(true);

        try {
            const response = await fetch(`/api/list-tables`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    }

    const handleListConstraints = async () => {
        const username = token.username;

        setIsLoading(true);

        try {
            const response = await fetch(`/api/list-constraints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                }),
            });

            const data = await response.json();
            console.log(data);
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    }

    const handleClearOutput = () => {
        setResult([]);
    }

    return (
        <>
            <p className="lead">Find the users who are called Dav</p>

            <SqlEditor onChange={setSqlText} onSubmit={handleExecute} />

            <div className="mt-3 support-buttons">
                <Button
                    className="btn-primary me-1"
                    disabled={isLoading || sqlText.trim().length === 0}
                    onClick={handleExecute}
                >
                    Execute
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                    onClick={handleShowSearchPath}
                >
                    Show Search Path
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                    onClick={handleListSchemas}
                >
                    List Schemas
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                    onClick={handleListTables}
                >
                    List Tables
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                    onClick={handleListConstraints}
                >
                    List Constraints
                </Button>

                <Button
                    className="btn-primary"
                    disabled={isLoading}
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
                            builtin={val.builtin}
                            queryId={val.id}
                            query={val.query}
                            success={val.success}
                            message={val.type === 'message'}
                        />
                    ))
                }
            </div>
        </>
    );
}

export default Query;