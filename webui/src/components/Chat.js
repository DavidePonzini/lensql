import { useState } from "react";
import useToken from "../hooks/useToken";
import MessageBox from "./MessageBox";
import Button from "./Button";


function Chat({ queryId, success }) {
    const [token] = useToken();

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

        try {
            const response = await fetch('/api/describe-my-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            console.log(data);
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    async function handleExplainQuery() {
        addMessage("Explain what each clause in my query is doing", false);
        startThinking();

        try {
            const response = await fetch('/api/explain-my-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    async function handleExplainError() {
        addMessage("Explain what this error means", false);
        startThinking();

        try {
            const response = await fetch('/api/explain-error-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    async function handleShowExample() {
        addMessage("Show a simplified example that can cause this problem", false);
        startThinking();

        try {
            const response = await fetch('/api/provide-error-example', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    async function handleWhereToLook() {
        addMessage("Show me which query part is causing this error", false);
        startThinking();

        try {
            const response = await fetch('/api/locate-error-cause', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    async function handleSuggestFix() {
        addMessage("Suggest a fix for this error", false);
        startThinking();

        try {
            const response = await fetch('/api/fix-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    'query_id': queryId,
                    'msg_idx': getLastMessageIdx(),
                })

            });

            const data = await response.json();

            stopThinking();
            addMessage(data.answer, true, false, data.id);
        } catch (error) {
            stopThinking();
            addMessage(`Error: ${error}`, true);
        } finally {
            addFollowupPrompt();
        }
    }

    return (
        <div>
            {messages.map((message, index) => (
                <MessageBox
                    assistant={message.isFromAssistant}
                    thinking={message.isThinking}
                    text={message.text}
                    messageId={message.messageId}
                >
                    {/* Buttons -- shown only on last message when not thinking */}
                    {!isThinking && index === messages.length - 1 && (
                        <div className="mt-2">
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
                        </div>
                    )}
                </MessageBox>
            ))}
        </div>
    );
}

export default Chat;