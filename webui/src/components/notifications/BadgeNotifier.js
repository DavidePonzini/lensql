import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import useUserInfo from '../../hooks/useUserInfo';

import BubbleMessage from './BubbleMessage';

let _setBadges = null;

function BadgeNotifier() {
    const [queue, setQueue] = useState([]);
    const { incrementStats } = useUserInfo();
    const { t } = useTranslation();

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

    if (!reward) return null;

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
                <i className="fas fa-trophy"></i>&nbsp;{t('components.notifications.badge.title')}
            </strong>

            {reward.reason ? (
                <>
                    <br />
                    {t(`gamification.badges.${reward.reason.split('.')[0]}.levels.${reward.reason.split('.')[1]}`)}
                </>
            ) : null}

            {reward.experience ? (
                <>
                    <br />
                    <span className='text text-primary'>
                        {reward.experience >= 0 ? '+' : '-'}
                        {t('components.notifications.badge.exp', { count: Math.abs(reward.experience) })} <i className="fa fa-diamond" />
                    </span>
                </>
            ) : null}

            {reward.coins ? (
                <>
                    <br />
                    <span className='text text-warning'>
                        {reward.coins >= 0 ? '+' : '-'}
                        {t('components.notifications.badge.coins', { count: Math.abs(reward.coins) })} <i className="fa fa-coins" />
                    </span>
                </>
            ) : null}
        </BubbleMessage>
    );
}

function setBadges(badges) {
    if (_setBadges) {
        _setBadges(badges);
    } else {
        console.warn('BadgeNotifier not mounted yet');
    }
}

export default BadgeNotifier;
export { BadgeNotifier, setBadges };
