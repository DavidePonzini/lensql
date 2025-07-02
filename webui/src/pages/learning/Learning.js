import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import QueryOverview from "./Queries";
import MessagesOverview from "./Messages";
import ErrorPatterns from "./Errors";

function Learning() {
    const { apiRequest, userInfo } = useAuth();
    const [queriesCount, setQueriesCount] = useState(0);

    useEffect(() => {
        async function fetchProfileData() {
            const response = await apiRequest('/api/users/stats/unique_queries', 'GET');
            setQueriesCount(response.data);
        }

        fetchProfileData();
    }, [apiRequest]);


    let welcomeMessage = "Here's a look at your SQL progress";
    if (queriesCount > 100) {
        welcomeMessage += " — keep going strong!";
    }

    return (
        <div className="container-md">
            <h1 className="display-3">Welcome back, {userInfo?.username || 'user'}!</h1>
            <p className="lead">{welcomeMessage}</p>

            <hr />
            <h2 id="queries">Let's look at your queries</h2>
            <QueryOverview />

            <hr />
            <h2 id="messages">Turning Questions Into Progress</h2>
            <MessagesOverview />

            <hr />
            <h2 id="errors">Where things got tricky</h2>
            <ErrorPatterns />
        </div>
    );
}

export default Learning;