import { useTranslation } from 'react-i18next';
import BubbleMessage from "./BubbleMessage";
import useUserInfo from "../hooks/useUserInfo";

function BubbleStatsChange({ rewards, setRewards, isAlert = true, style = {}, duration = 2000 }) {
    const { incrementStats } = useUserInfo();
    const { t } = useTranslation();

    const reward = rewards[0] || null;

    if (!reward) return null;

    const coinLabel = Math.abs(reward.coins) === 1
        ? t('reward.coin_singular')
        : t('reward.coin_plural');

    return (
        <>
            <BubbleMessage
                className={isAlert ? "alert alert-warning" : "text text-warning"}
                visible={reward.coins !== 0}
                onHide={() => {
                    incrementStats(reward.coins, 0);
                    reward.coins = 0;

                    if (reward.experience === 0)
                        setRewards(prev => prev.slice(1));
                }}
                style={style}
                duration={duration}
            >
                {reward.reason ? (
                    <>
                        <strong>{reward.reason}:&nbsp;</strong>
                    </>
                ) : null}
                {reward.coins >= 0 ? '+' : '-'}{Math.abs(reward.coins)} {coinLabel} <i className="fa fa-coins" />
            </BubbleMessage>

            <BubbleMessage
                className={isAlert ? "alert alert-primary" : "text text-primary"}
                visible={reward.coins === 0 && reward.experience !== 0}
                onHide={() => {
                    incrementStats(0, reward.experience);
                    setRewards(prev => prev.slice(1));
                }}
                style={style}
                duration={duration}
            >
                {reward.reason ? (
                    <>
                        <strong>{reward.reason}:&nbsp;</strong>
                    </>
                ) : null}
                {reward.experience >= 0 ? '+' : '-'}{t('reward.exp', { count: Math.abs(reward.experience) })} <i className="fa fa-diamond" />
            </BubbleMessage>
        </>
    );
}

export default BubbleStatsChange;
