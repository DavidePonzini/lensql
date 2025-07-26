import { useState, useRef } from "react";
import useAuth from "../../hooks/useAuth";
import MessageBox from "./MessageBox";
import ButtonAction from "../../components/ButtonAction";
import BubbleStatsChange from "../../components/BubbleStatsChange";
import { setBadges } from "../../components/BadgeNotifier";

import { Coins } from "../../constants/Gamification";


function Chat({ queryId, success }) {
    const { apiRequest } = useAuth();

    const [messages, setMessages] = useState([
        {
            text: 'Would you like to ask me anything about this result?',
            isFromAssistant: true,
            isThinking: false,
            messageId: null,
        }
    ]);
    const [rewards, setRewards] = useState([]);

    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef(null);

    const buttonSuccessDescribeLocked = false;
    const buttonSuccessExplainLocked = false;
    const buttonErrorExplainLocked = false;
    const buttonErrorExampleLocked = false;
    const buttonErrorLocateLocked = false;
    const buttonErrorFixLocked = false;

    function addMessage(text, isFromAssistant, isThinking = false, messageId = null) {
        setMessages((prevMessages) => [...prevMessages, {
            text,
            isFromAssistant,
            isThinking,
            messageId,
        }]);
    };

    function addFollowupPrompt() {
        addMessage('Would you like to ask something else?', true);
    }

    function removeLastMessage() {
        setMessages((prevMessages) => prevMessages.slice(0, -1));
    }

    function startThinking() {
        addMessage("Thinking...", true, true);
        setIsThinking(true);
    }

    function stopThinking() {
        removeLastMessage();
        setIsThinking(false);
    }

    function getLastMessageIdx() {
        return messages.filter(m => !m.isFromAssistant).length;
    };

    async function handleDescribeQuery() {
        addMessage("Describe what my query does", false);
        startThinking();

        const data = await apiRequest('/api/messages/success/describe', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        console.log("Describe query response:", data);

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleExplainQuery() {
        addMessage("Explain what each clause in my query is doing", false);
        startThinking();

        const data = await apiRequest('/api/messages/success/explain', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleExplainError() {
        addMessage("Explain what this error means", false);
        startThinking();

        const data = await apiRequest('/api/messages/error/explain', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        stopThinking();
        focusOnLastUserMessage();
        addMessage(data.answer, true, false, data.id);
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleShowExample() {
        addMessage("Show a simplified example that can cause this problem", false);
        startThinking();

        const data = await apiRequest('/api/messages/error/example', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleWhereToLook() {
        addMessage("Show me which query part is causing this error", false);
        startThinking();

        const data = await apiRequest('/api/messages/error/locate', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleSuggestFix() {
        addMessage("Suggest a fix for this error", false);
        startThinking();

        const data = await apiRequest('/api/messages/error/fix', 'POST', {
            'query_id': queryId,
            'msg_idx': getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    function focusOnLastUserMessage() {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }


    return (
        <div id={`chat-${queryId}`}>
            {messages.map((message, index) => (
                <MessageBox
                    assistant={message.isFromAssistant}
                    thinking={message.isThinking}
                    text={message.text}
                    messageId={message.messageId}
                    key={index}
                    ref={index === messages.length - 1 ? messagesEndRef : null}
                >
                    {/* Buttons -- shown only on last message when not thinking */}
                    {!isThinking && index === messages.length - 1 && (
                        <div className="mt-2">
                            {success ? (
                                <>
                                    <ButtonAction
                                        onClick={handleDescribeQuery}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_SUCCESS_DESCRIBE}
                                        locked={buttonSuccessDescribeLocked}
                                    >
                                        Describe query
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleExplainQuery}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_SUCCESS_EXPLAIN}
                                        locked={buttonSuccessExplainLocked}
                                    >
                                        Explain query
                                    </ButtonAction>
                                </>
                            ) : (
                                <>
                                    <ButtonAction
                                        onClick={handleExplainError}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_EXPLAIN}
                                        locked={buttonErrorExplainLocked}
                                    >
                                        Explain error
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleShowExample}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_EXAMPLE}
                                        locked={buttonErrorExampleLocked}
                                    >
                                        Show example
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleWhereToLook}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_LOCATE}
                                        locked={buttonErrorLocateLocked}
                                    >
                                        Where to look
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleSuggestFix}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_FIX}
                                        locked={buttonErrorFixLocked}
                                    >
                                        Suggest fix
                                    </ButtonAction>
                                </>
                            )}
                        </div>
                    )}
                </MessageBox>
            ))}

            <div style={{
                marginLeft: '70px',
                marginTop: '.5rem',
            }}>
                <BubbleStatsChange
                    rewards={rewards}
                    setRewards={setRewards}
                    style={{ padding: '6px' }}
                />
            </div>
        </div>
    );
}

export default Chat;