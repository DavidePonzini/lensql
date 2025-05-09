import MessageBox from "./MessageBox";
import Button from "./Button";


function Chat({ messages, success }) {
    const handleExplainError = () => {
        console.log("Explain error");
    }

    return (
        <div>
            <MessageBox assistant={true}>
                Would you like to ask me anything about this result?
            </MessageBox>

            {messages.map((message, index) => (
                <MessageBox>
                    {message}
                </MessageBox>
            ))}

            {success ? (
                <>
                    <Button className="btn-primary me-2" onClick={handleExplainError}>
                        Describe query
                    </Button>

                    <Button className="btn-primary me-2" onClick={handleExplainError} disabled={true}>
                        Explain query
                    </Button>
                </>
            ) : (
                <>
                    <Button className="btn-primary me-2" onClick={handleExplainError}>
                        Explain error
                    </Button>

                    <Button className="btn-primary me-2" onClick={handleExplainError} disabled={true}>
                        Show example
                    </Button>

                    <Button className="btn-primary me-2" onClick={handleExplainError}>
                        Where to look
                    </Button>

                    <Button className="btn-primary me-2" onClick={handleExplainError}>
                        Suggest fix
                    </Button>
                </>
            )}
        </div>
    );
}

export default Chat;