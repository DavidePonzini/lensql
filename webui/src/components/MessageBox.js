import Message from './Message';

function MessageBox({ children, assistant = false, feedback = false }) {
    return (
        <div className={`messagebox ${assistant ? 'messagebox-assistant' : 'messagebox-user'}`}>
            {assistant && (
                <div className="icon">
                    <i className="fas fa-search" />
                    <br />
                    LensQL
                </div>
            )}

            <Message feedback={feedback}>
                {children}
            </Message>

            {!assistant && (
                <div className="icon">
                    <i className="fas fa-user" />
                    <br />
                    You
                </div>
            )}
        </div>
    );
}

export default MessageBox;