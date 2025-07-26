import { useEffect, useState } from 'react';
import BubbleMessage from './BubbleMessage';
import useUserInfo from '../hooks/useUserInfo';

let _setBadges = null; // mutable reference accessible globally

function BadgeNotifier() {
    const [queue, setQueue] = useState([]);
    const { incrementStats } = useUserInfo();

    const duration = 3000;

    function setBadges(badges) {
        if (!badges || !badges.length) return;
        setQueue(prev => prev.concat(badges));
    }

    useEffect(() => {
        _setBadges = setBadges;
        return () => { _setBadges = null };
    }, []);

    const reward = queue.length ? queue[0] : null;

    if (!reward)
        return null;

    return (
        <BubbleMessage
            className="alert alert-success"
            visible={true}
            duration={duration}
            onHide={() => {
                incrementStats(reward.coins || 0, reward.experience || 0);
                setQueue(prev => prev.slice(1));
            }}
            style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                zIndex: 9999,
                minWidth: '250px'
            }}
        >
            <strong className='lead'>
                <i className="fas fa-trophy"></i>&nbsp;Achievement Unlocked!
            </strong>

            {reward.reason ? (
                <>
                    <br />
                    {reward.reason}
                </>
            ) : null}

            {reward.experience ? (
                <>
                    <br />
                    <span className='text text-primary'>
                        {reward.experience >= 0 ? '+' : '-'}{Math.abs(reward.experience)} EXP <i className="fa fa-diamond" />
                    </span>
                </>
            ) : null}

            {reward.coins ? (
                <>
                    <br />
                    <span className='text text-warning'>
                        {reward.coins >= 0 ? '+' : '-'}{Math.abs(reward.coins)} LensCoins <i className="fa fa-coins" />
                    </span>
                </>
            ) : null}
        </BubbleMessage>
    );
}

// Trigger function (safe fallback if component not mounted)
function setBadges(badges) {
    if (_setBadges) {
        _setBadges(badges);
    } else {
        console.warn('BadgeNotifier not mounted yet');
    }
}

export default BadgeNotifier;
export { BadgeNotifier, setBadges };