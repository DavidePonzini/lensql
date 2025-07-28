import useGamificationData from "../../hooks/useGamificationData";

function UserLevelTitle({ level }) {
    const { getLevelTitle } = useGamificationData();

    return (
        <span>
            {level} <i>({getLevelTitle(level)})</i>
        </span>
    );
}

export default UserLevelTitle;
