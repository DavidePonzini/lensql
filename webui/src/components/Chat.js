import { useState } from "react";
import MessageBox from "./MessageBox";
import Button from "./Button";


function Chat({ success }) {
    const [messages, setMessages] = useState([
        {
            text: 'Would you like to ask me anything about this result?',
            isFromAssistant: true,
            askFeedback: false,
            thinking: false,
        }
    ]);
    const [isThinking, setIsThinking] = useState(false);

    const addMessage = (text, isFromAssistant, askFeedback = false, thinking = false) => {
        setMessages((prevMessages) => [...prevMessages, {
            text,
            isFromAssistant,
            askFeedback,
            thinking,
        }]);
    }

    const removeLastMessage = () => {
        setMessages((prevMessages) => prevMessages.slice(0, -1));
    }

    const startThinking = () => {
        addMessage("Thinking...", true, false, true);
        setIsThinking(true);
    }

    const stopThinking = () => {
        removeLastMessage();
        setIsThinking(false);
    }

    const handleExplainQuery = () => {
        addMessage("Explain query", false);
        startThinking();
    }

    const handleDescribeQuery = () => {
        addMessage("Describe query", false);
        startThinking();
    }

    const handleExplainError = () => {
        addMessage("Explain error", false);
        startThinking();
    }

    const handleShowExample = () => {
        addMessage("Show example", false);
        startThinking();
    }

    const handleWhereToLook = () => {
        addMessage("Where to look", false);
        startThinking();
    }

    const handleSuggestFix = () => {
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

                            <Button className="btn-primary me-2" onClick={handleExplainError}>
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