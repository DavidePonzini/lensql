import Message from './Message';

import './MessageBox.css';

function MessageBox({ children, text, assistant = false, thinking = false, messageId = null }) {

    return (
        <div className={`messagebox ${assistant ? 'messagebox-assistant' : 'messagebox-user'} ${thinking ? 'thinking' : ''}`}>
            {assistant && (
                <div className="icon">
                    <i className="fas fa-search" />
                    <br />
                    LensQL
                </div>
            )}

            <Message messageId={messageId} text={text}>
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