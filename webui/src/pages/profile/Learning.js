import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import LearningStatsQueries from "../../components/LearningStatsQueries";
import LearningStatsMessages from "../../components/LearningStatsMessages";
import LearningStatsErrors from "../../components/LearningStatsErrors";

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
            <LearningStatsQueries />

            <hr />
            <h2 id="messages">Turning Questions Into Progress</h2>
            <LearningStatsMessages />

            <hr />
            <h2 id="errors">Where things got tricky</h2>
            <LearningStatsErrors />
        </div>
    );
}

export default Learning;