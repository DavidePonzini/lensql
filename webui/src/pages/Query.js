import { useState } from "react";
import useToken from "../hooks/useToken";

import '../styles/Query.css';

import SqlEditor from "../components/SqlEditor";
import Button from "../components/Button";

function Query() {
    const [sqlText, setSqlText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [token, setToken] = useToken();

    const displayResult = (data) => {
        setResult(data);
        if (!data) return null;

        console.log(data);
    }

    const handleExecute = async () => {
        console.log("Executing SQL query:", sqlText);
        if (!sqlText.trim()) return;
        console.log(2)

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
                >
                    Show Search Path
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                >
                    List Schemas
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                >
                    List Tables
                </Button>

                <Button
                    className="btn-secondary me-1"
                    disabled={isLoading}
                >
                    List Constraints
                </Button>

                <Button
                    className="btn-primary"
                >
                    Clear output
                </Button>
            </div>

            <div className="mt-3">
                <div id="result"></div>
            </div>
        </>
    );
}

export default Query;