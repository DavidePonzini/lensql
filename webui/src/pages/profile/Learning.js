import useUserInfo from "../../hooks/useUserInfo";
import LearningStatsAll from "../../components/LearningStatsAll";

function Learning() {
    const { userInfo } = useUserInfo();

    return (
        <div className="container-md">
            <h1 className="display-3">Welcome back, {userInfo?.username || 'user'}!</h1>
            <p className="lead">Here's a look at your SQL progress</p>

            <hr />
            <LearningStatsAll />
        </div>
    );
}

export default Learning;