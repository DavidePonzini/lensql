import { getLevelTitle } from '../../constants/Gamification';

function UserLevelTitle({ level }) {
    return (
        <span>
            {level} <i>({getLevelTitle(level)})</i>
        </span>
    );
}

export default UserLevelTitle;
