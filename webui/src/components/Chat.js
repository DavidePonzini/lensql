import { useState } from "react";
import useAuth from "../hooks/useAuth";
import MessageBox from "./MessageBox";


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
    const [isThinking, setIsThinking] = useState(false);

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

        stopThinking();
        addMessage(data.answer, true, false, data.id);
        focusOnLastUserMessage();
        addFollowupPrompt();
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
    }

    function focusOnLastUserMessage() {
        // TODO does not select the last message for user 
        // messagebox-user works, but selects the first
        // messagebox-user:last-child returns null
        const lastUserMessage = document.querySelector(`#chat-${queryId} .messagebox.messagebox-user:last-child`);  

        if (lastUserMessage) {
            lastUserMessage.scrollIntoView({ behavior: 'smooth' });
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
                    {/* Buttons -- shown only on last message when not thinking */}
                    {!isThinking && index === messages.length - 1 && (
                        <div className="mt-2">
                            {success ? (
                                <>
                                    <button className="btn btn-primary me-2" onClick={handleDescribeQuery}>
                                        Describe query
                                    </button>

                                    <button className="btn btn-primary me-2" onClick={handleExplainQuery}>
                                        Explain query
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button className="btn btn-primary me-2" onClick={handleExplainError}>
                                        Explain error
                                    </button>

                                    <button className="btn btn-primary me-2" onClick={handleShowExample} disabled={true}>
                                        Show example
                                    </button>

                                    <button className="btn btn-primary me-2" onClick={handleWhereToLook}>
                                        Where to look
                                    </button>

                                    <button className="btn btn-primary me-2" onClick={handleSuggestFix}>
                                        Suggest fix
                                    </button>
                                </>
                            )}
                        </div>
                    )}
                </MessageBox>
            ))}
        </div>
    );
}

export default Chat;