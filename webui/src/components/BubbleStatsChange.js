import BubbleMessage from "./BubbleMessage";

function BubbleStatsChange({
    coinsChange = 0, setCoinsChange = (val) => { },
    expChange = 0, setExpChange = (val) => { },
    isAlert = true,
    changeReason = '',
    style = {}
}) {
    const duration = 2000;

    return (
        <>
            <BubbleMessage
                className={isAlert ? "alert alert-warning" : "text text-warning"}
                visible={coinsChange !== 0}
                onHide={() => setCoinsChange(0)}
                style={style}
                duration={duration}
            >
                {changeReason ? (
                    <>
                        <strong>{changeReason}:</strong>&nbsp;
                    </>
                ) : null}

                {coinsChange >= 0 ? '+' : '-'}{Math.abs(coinsChange)} {Math.abs(coinsChange) === 1 ? 'LensCoin' : 'LensCoins'} <i className="fa fa-coins" />
            </BubbleMessage>

            <BubbleMessage
                className={isAlert ? "alert alert-primary" : "text text-primary"}
                visible={coinsChange === 0 && expChange !== 0}
                onHide={() => setExpChange(0)}
                style={style}
                duration={duration}
            >
                {changeReason ? (
                    <>
                        <strong>{changeReason}:</strong>&nbsp;
                    </>
                ) : null}
                
                {expChange >= 0 ? '+' : '-'}{Math.abs(expChange)} EXP <i className="fa fa-diamond" />
            </BubbleMessage>
        </>
    );
}

export default BubbleStatsChange;