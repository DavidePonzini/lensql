import { useState, useRef } from "react";
import { useTranslation } from "react-i18next";

import useAuth from "../../hooks/useAuth";
import useGamificationData from "../../hooks/useGamificationData";

import ButtonAction from "../../components/buttons/ButtonAction";
import BubbleStatsChange from "../../components/notifications/BubbleStatsChange";
import { setBadges } from "../../components/notifications/BadgeNotifier";

import MessageBox from "./MessageBox";

function Chat({ queryId, success }) {
    const { apiRequest } = useAuth();
    const { Coins } = useGamificationData();
    const { t } = useTranslation();

    const [messages, setMessages] = useState([
        {
            text: t('pages.exercises.chat.initial_prompt'),
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
    const buttonSuccessCheckErrorsLocked = false;
    const buttonErrorExplainLocked = false;
    const buttonErrorExampleLocked = false;
    const buttonErrorLocateLocked = false;
    const buttonErrorFixLocked = false;

    function addMessage(text, isFromAssistant, isThinking = false, messageId = null) {
        setMessages(prev => [...prev, { text, isFromAssistant, isThinking, messageId }]);
    }

    function removeLastMessage() {
        setMessages(prev => prev.slice(0, -1));
    }

    function startThinking() {
        addMessage(t('pages.exercises.chat.thinking'), true, true);
        setIsThinking(true);
    }

    function stopThinking() {
        removeLastMessage();
        setIsThinking(false);
    }

    function getLastMessageIdx() {
        return messages.filter(m => !m.isFromAssistant).length;
    }

    async function handleDescribeQuery() {
        addMessage(t('pages.exercises.chat.prompts.describe'), false);
        startThinking();

        const data = await apiRequest('/api/messages/success/describe', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleExplainQuery() {
        addMessage(t('pages.exercises.chat.prompts.explain'), false);
        startThinking();

        const data = await apiRequest('/api/messages/success/explain', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleCheckErrors() {
        addMessage(t('pages.exercises.chat.prompts.detect_errors'), false);
        startThinking();

        const data = await apiRequest('/api/messages/success/detect-errors', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleExplainError() {
        addMessage(t('pages.exercises.chat.prompts.explain_error'), false);
        startThinking();

        const data = await apiRequest('/api/messages/error/explain', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        focusOnLastUserMessage();
        addMessage(data.answer, true, false, data.id);
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleShowExample() {
        addMessage(t('pages.exercises.chat.prompts.example'), false);
        startThinking();

        const data = await apiRequest('/api/messages/error/example', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleWhereToLook() {
        addMessage(t('pages.exercises.chat.prompts.locate'), false);
        startThinking();

        const data = await apiRequest('/api/messages/error/locate', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
        });

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
        setRewards(data.rewards || []);
        setBadges(data.badges || []);
    }

    async function handleSuggestFix() {
        addMessage(t('pages.exercises.chat.prompts.fix'), false);
        startThinking();

        const data = await apiRequest('/api/messages/error/fix', 'POST', {
            query_id: queryId,
            msg_idx: getLastMessageIdx(),
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
                >
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
                                        {t('pages.exercises.chat.buttons.describe')}
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleExplainQuery}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_SUCCESS_EXPLAIN}
                                        locked={buttonSuccessExplainLocked}
                                    >
                                        {t('pages.exercises.chat.buttons.explain')}
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleCheckErrors}
                                        className="me-2 mb-1"
                                        variant="warning"
                                        cost={-Coins.HELP_SUCCESS_CHECK_ERRORS}
                                        locked={buttonSuccessCheckErrorsLocked}
                                    >
                                        {t('pages.exercises.chat.buttons.detect_errors')}
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
                                        {t('pages.exercises.chat.buttons.explain_error')}
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleShowExample}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_EXAMPLE}
                                        locked={buttonErrorExampleLocked}
                                    >
                                        {t('pages.exercises.chat.buttons.example')}
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleWhereToLook}
                                        className="me-2 mb-1"
                                        variant="primary"
                                        cost={-Coins.HELP_ERROR_LOCATE}
                                        locked={buttonErrorLocateLocked}
                                    >
                                        {t('pages.exercises.chat.buttons.locate')}
                                    </ButtonAction>

                                    <ButtonAction
                                        onClick={handleSuggestFix}
                                        className="me-2 mb-1"
                                        variant="warning"
                                        cost={-Coins.HELP_ERROR_FIX}
                                        locked={buttonErrorFixLocked}
                                    >
                                        {t('pages.exercises.chat.buttons.fix')}
                                    </ButtonAction>
                                </>
                            )}
                        </div>
                    )}
                </MessageBox>
            ))}

            <div
                ref={messagesEndRef}
                style={{
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
