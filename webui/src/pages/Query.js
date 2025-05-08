import { useState } from "react";
import SqlEditor from "../components/SqlEditor";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Separator from "../components/Separator";
import Button from "../components/Button";

function Query() {
    const [sqlText, setSqlText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);

    const displayResult = (data) => {
        setResult(data);
        if (!data) return null;

        console.log(data);
    }

    const handleExecute = async () => {
        console.log("Executing SQL query:", sqlText);
        if (!sqlText.trim()) return;
        console.log(2)

        const username = 'dav';
        setIsLoading(true);

        try {
            const response = await fetch(`/api/run-query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: JSON.stringify(username),
                    query: JSON.stringify(sqlText),
                }),
            });

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            alert("Could not connect to server.");
        } finally {
            setIsLoading(false);
        }
    };


    return (
        <>
            <Navbar />

            <div className="content">
                <div className="container-md">
                    <p className="lead">Find the users who are called Dav</p>

                    <SqlEditor onChange={setSqlText} />

                    <div className="mt-3">
                        <Button
                            className="btn-primary"
                            disabled={isLoading || sqlText.trim().length === 0}
                            onClick={handleExecute}>
                            Execute
                        </Button>
                        <Button className="btn-secondary" disabled={isLoading}>Show Search Path</Button>
                        <Button className="btn-secondary" disabled={isLoading}>List Schemas</Button>
                        <Button className="btn-secondary" disabled={isLoading}>List Tables</Button>
                        <Button className="btn-primary">Clear output</Button>
                    </div>

                    <div className="mt-3">
                        <div id="result"></div>
                    </div>
                </div>
            </div>

            <Separator />
            <Footer />
        </>
    );
}

export default Query;