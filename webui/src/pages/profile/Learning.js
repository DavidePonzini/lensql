import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import LearningStatsAll from "../../components/LearningStatsAll";

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
            <LearningStatsAll />
        </div>
    );
}

export default Learning;