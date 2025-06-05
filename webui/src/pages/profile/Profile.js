import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import QueryOverview from "./Queries";
import MessagesOverview from "./Messages";
import ErrorPatterns from "./Errors";

function Profile() {
    const { apiRequest, userInfo } = useAuth();
    const [profileData, setProfileData] = useState(null);

    useEffect(() => {
        async function fetchProfileData() {
            const response = await apiRequest('/api/users/learning-stats', 'GET');
            setProfileData(response.data)
        }

        fetchProfileData();
    }, [apiRequest]);   // eslint-disable-line react-hooks/exhaustive-deps

    const uniqueQueries = profileData?.queries_d || 0;

    let welcomeMessage;
    if (uniqueQueries === 0) {
        welcomeMessage = "It looks like you haven't run any queries yet. Don't worry, every expert was once a beginner! Start by trying out some basic SQL commands to get the hang of it.";
    } else if (uniqueQueries < 10) {
        welcomeMessage = "You're off to a great start! Keep experimenting with different queries to build your SQL skills. Remember, practice makes perfect!";
    } else {
        welcomeMessage = "Here's a quick look at your SQL progress — keep going strong!";
    }

    return (
        <>
            <h1 className="display-3">Welcome back, {userInfo?.username || 'user'}!</h1>
            <p className="lead">{welcomeMessage}</p>

            <hr />
            <h2>Let's look at your queries</h2>
            <QueryOverview data={profileData} />

            <hr />
            <h2>Turning Questions Into Progress</h2>
            <MessagesOverview data={profileData} />

            <hr />
            <h2>Where things got tricky</h2>
            <ErrorPatterns data={profileData} />
        </>
    );
}

export default Profile;