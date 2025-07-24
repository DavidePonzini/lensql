import { useState } from 'react';
import useAuth from '../../hooks/useAuth';
import BubbleStatsChange from '../../components/BubbleStatsChange';
import { Coins } from '../../constants/Gamification';

import './Message.css';

function Message({ children, text, messageId = null }) {
    const { apiRequest, incrementStats } = useAuth();

    const [feedback, setFeedback] = useState(null);
    const [coinsChange, setCoinsChange] = useState(0);

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

        await apiRequest('/api/messages/feedback', 'POST', {
            'message_id': messageId,
            'feedback': positive
        });

        sessionStorage.setItem('hasProvidedFeedback', 'true');
        setFeedback(positive);

        incrementStats(Coins.HELP_FEEDBACK, 0);
        setCoinsChange(Coins.HELP_FEEDBACK);
    }

    return (
        <div className="message" >
            <div dangerouslySetInnerHTML={{ __html: text }} />

            {
                messageId && (
                    <div className="message-feedback">
                        <BubbleStatsChange
                            coinsChange={coinsChange}
                            setCoinsChange={setCoinsChange}
                            isAlert={false}
                            changeReason='Provided feedback'
                        />

                        {
                            !sessionStorage.getItem('hasProvidedFeedback') && (
                                <span className="text-muted">
                                    You can earn {Coins.HELP_FEEDBACK} LensCoins by providing feedback on this message
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