import { useState } from 'react';
import useAuth from '../hooks/useAuth';

import '../styles/Message.css';

function Message({ children, text, messageId = null }) {
    const { apiRequest } = useAuth();

    const [feedback, setFeedback] = useState(null);

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

        await apiRequest('/api/message-feedback', 'POST', {
            'message_id': messageId,
            'feedback': positive
        });

        setFeedback(positive);
    }

    return (
        <div className="message" >
            <div dangerouslySetInnerHTML={{ __html: text }} />

            {
                messageId && (
                    <div className="message-feedback">
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