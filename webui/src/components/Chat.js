import { useState } from "react";
import MessageBox from "./MessageBox";
import Button from "./Button";


function Chat({ queryId, success }) {
    const [messages, setMessages] = useState([
        {
            text: 'Would you like to ask me anything about this result?',
            isFromAssistant: true,
            askFeedback: false,
            thinking: false,
        }
    ]);
    const [isThinking, setIsThinking] = useState(false);

    function addMessage(text, isFromAssistant, askFeedback = false, thinking = false, message_id = null) {
        setMessages((prevMessages) => [...prevMessages, {
            text,
            isFromAssistant,
            askFeedback,
            thinking,
            message_id,
        }]);
    };

    function removeLastMessage() {
        setMessages((prevMessages) => prevMessages.slice(0, -1));
    }

    function startThinking() {
        addMessage("Thinking...", true, false, true);
        setIsThinking(true);
    }

    function stopThinking() {
        removeLastMessage();
        setIsThinking(false);
    }

    function getLastMessageIdx() {
        return messages.filter(m => !m.thinking).length;
    };

    async function handleExplainQuery() {
        addMessage("Explain query", false);
        startThinking();

        try {
            const response = await fetch('/api/explain-my-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, true, false, data.message_id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        }
    }

    async function handleDescribeQuery() {
        addMessage("Describe query", false);
        startThinking();
    }

    async function handleExplainError() {
        addMessage("Explain error", false);
        startThinking();
    }

    async function handleShowExample() {
        addMessage("Show example", false);
        startThinking();
    }

    async function handleWhereToLook() {
        addMessage("Where to look", false);
        startThinking();
    }

    async function handleSuggestFix() {
        addMessage("Suggest fix", false);
        startThinking();
    }

    return (
        <div>
            {messages.map((message, index) => (
                <MessageBox
                    assistant={message.isFromAssistant}
                    feedback={message.askFeedback}
                    thinking={message.thinking}
                >
                    {message.text}
                </MessageBox>
            ))}

            {/* Buttons -- shown only when not thinking */}
            {!isThinking && (
                <>
                    {success ? (
                        <>
                            <Button className="btn-primary me-2" onClick={handleDescribeQuery}>
                                Describe query
                            </Button>

                            <Button className="btn-primary me-2" onClick={handleExplainQuery}>
                                Explain query
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button className="btn-primary me-2" onClick={handleExplainError}>
                                Explain error
                            </Button>

                            <Button className="btn-primary me-2" onClick={handleShowExample} disabled={true}>
                                Show example
                            </Button>

                            <Button className="btn-primary me-2" onClick={handleWhereToLook}>
                                Where to look
                            </Button>

                            <Button className="btn-primary me-2" onClick={handleSuggestFix}>
                                Suggest fix
                            </Button>
                        </>
                    )}
                </>
            )}
        </div>
    );
}

export default Chat;