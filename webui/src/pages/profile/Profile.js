import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import LevelTitle from "./LevelTitle";

function Profile() {
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
            <p style={{ color: 'red', fontWeight: 'bold' }}>This section is under developent</p>

            <hr />

            <p>
                <i className="fa fa-shield me-1" />
                Current Level: <LevelTitle level={userInfo?.level || 0} />
            </p>
            <p>
                <i className="fa fa-trophy me-1" />
                EXP: {userInfo?.xp || 0}/{userInfo?.xpToNextLevel || 0}
            </p>
            <p>
                <i className="fa fa-coins me-1" />
                LensCoins: {userInfo?.coins || 0}
            </p>

            <hr />
            <h2>Achievements</h2>
            <ul className="list-group mb-3">
                <li className="list-group-item d-flex justify-content-between align-items-center">
                    First Query
                    <span className="badge bg-success rounded-pill">Unlocked</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                    100 Queries
                    <span className="badge bg-secondary rounded-pill">Locked</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                    SQL Master
                    <span className="badge bg-secondary rounded-pill">Locked</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                    LensCoins Collector
                    <span className="badge bg-secondary rounded-pill">Locked</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                    Daily Challenger
                    <span className="badge bg-secondary rounded-pill">Locked</span>
                </li>
            </ul>
        </div>
    );
}

export default Profile;