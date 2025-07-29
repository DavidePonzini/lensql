import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

import BubbleStatsChange from '../../components/notifications/BubbleStatsChange';
import { setBadges } from '../../components/notifications/BadgeNotifier';

import './Message.css';

function Message({ children, text, messageId = null }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();

    const [feedback, setFeedback] = useState(null);
    const [rewards, setRewards] = useState([]);

    async function handleSendFeedback(positive) {
        // This message doesn't support feedback
        if (!messageId) {
            return;
        }

        // Feedback is already sent
        // and we don't want to send it again
        if (feedback !== null) {
            return;
        }

        const result = await apiRequest('/api/messages/feedback', 'POST', {
            'message_id': messageId,
            'feedback': positive
        });

        sessionStorage.setItem('hasProvidedFeedback', 'true');
        setFeedback(positive);

        setRewards(result.rewards || []);
        setBadges(result.badges || []);
    }

    return (
        <div className="message" >
            <div dangerouslySetInnerHTML={{ __html: text }} />

            {
                messageId && (
                    <div className="message-feedback">
                        <BubbleStatsChange
                            rewards={rewards}
                            setRewards={setRewards}
                            isAlert={false}
                        />

                        {
                            !sessionStorage.getItem('hasProvidedFeedback') && (
                                <span className="text-muted">
                                    {t('pages.exercises.message.feedback_invite')}
                                    <i className="fa fa-arrow-right mx-1" />
                                </span>
                            )
                        }

                        <span
                            className={`feedback feedback-up ${feedback !== null ? 'disabled' : ''} ${feedback === true ? 'selected' : ''}`}
                            data-bs-toggle="tooltip"
                            data-bs-placement="bottom"
                            data-bs-title="Helpful"
                            onClick={() => handleSendFeedback(true)}
                        >
                            <i className={`${feedback === true ? 'fas' : 'far'} fa-thumbs-up`} />
                        </span>

                        <span
                            className={`feedback feedback-down ${feedback !== null ? 'disabled' : ''} ${feedback === false ? 'selected' : ''}`}
                            data-bs-toggle="tooltip"
                            data-bs-placement="bottom"
                            data-bs-title="Not helpful"
                            onClick={() => handleSendFeedback(false)}
                        >
                            <i className={`${feedback === false ? 'fas' : 'far'} fa-thumbs-down`} />
                        </span>
                    </div>
                )
            }

            {children}
        </div >
    );
}

export default Message;