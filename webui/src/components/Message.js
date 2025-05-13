import { useState } from 'react';

import '../styles/Message.css';

function Message({ children, text, messageId = null }) {
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

        try {
            const response = await fetch('/api/message-feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'message_id': messageId,
                    'feedback': positive
                })
            });

            setFeedback(positive);
        } catch (error) {
            alert(`Error: ${error}`);
            console.error(error);
        }
    }

    return (
        <div className="message" >
            <div dangerouslySetInnerHTML={{ __html: text }} />

            {
                messageId && (
                    <div class="message-feedback">
                        <span
                            className={`feedback feedback-up ${feedback !== null ? 'disabled' : ''} ${feedback === true ? 'selected' : ''}`}
                            data-bs-toggle="tooltip"
                            data-bs-placement="bottom"
                            data-bs-title="Helpful"
                            onClick={() => handleSendFeedback(true)}
                        >
                            <i class={`${feedback === true ? 'fas' : 'far'} fa-thumbs-up`} />
                        </span>

                        <span
                            className={`feedback feedback-down ${feedback !== null ? 'disabled' : ''} ${feedback === false ? 'selected' : ''}`}
                            data-bs-toggle="tooltip"
                            data-bs-placement="bottom"
                            data-bs-title="Not helpful"
                            onClick={() => handleSendFeedback(false)}
                        >
                            <i class={`${feedback === false ? 'fas' : 'far'} fa-thumbs-down`} />
                        </span>
                    </div>
                )
            }

            {children}
        </div >
    );
}

export default Message;