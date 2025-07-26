import BubbleMessage from "./BubbleMessage";
import useUserInfo from "../hooks/useUserInfo";

function BubbleStatsChange({ rewards, setRewards, isAlert = true, style = {} }) {
    const { incrementStats } = useUserInfo();

    const duration = 2000;

    const reward = rewards[0] || null;

    if (!reward) {
        return null;
    }

    return (
        <>
            <BubbleMessage
                className={isAlert ? "alert alert-warning" : "text text-warning"}
                visible={reward.coins > 0}
                onHide={() => {
                    console.log('Incrementing coins:', reward.coins);
                    incrementStats(reward.coins, 0);
                    reward.coins = 0;

                    if (reward.experience === 0)
                        setRewards(prev => prev.slice(1));
                }}
                style={style}
                duration={duration}
            >
                {
                    reward.reason ? (
                        <>
                            <strong>{reward.reason}:</strong> &nbsp;
                        </>
                    ) : null}

                {reward.coins >= 0 ? '+' : '-'} {Math.abs(reward.coins)} {Math.abs(reward.coins) === 1 ? 'LensCoin' : 'LensCoins'} <i className="fa fa-coins" />
            </BubbleMessage >

            <BubbleMessage
                className={isAlert ? "alert alert-primary" : "text text-primary"}
                visible={reward.coins === 0 && reward.experience !== 0}
                onHide={() => {
                    console.log('Incrementing exp:', reward.experience);
                    incrementStats(0, reward.experience);
                    setRewards(prev => prev.slice(1));
                }}
                style={style}
                duration={duration}
            >
                {reward.reason ? (
                    <>
                        <strong>{reward.reason}:</strong>&nbsp;
                    </>
                ) : null}

                {reward.experience >= 0 ? '+' : '-'}{Math.abs(reward.experience)} EXP <i className="fa fa-diamond" />
            </BubbleMessage>
        </>
    );
}

export default BubbleStatsChange;