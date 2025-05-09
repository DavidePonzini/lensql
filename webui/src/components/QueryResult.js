import { useState } from "react";
import Chat from './Chat';

function QueryResult({ result, builtin, queryId, query, success, message }) {
    const [messages, setMessages] = useState([]);

    return (
        <div className={`chat alert ${builtin ? 'alert-secondary' : success ? 'alert-primary' : 'alert-danger'}`}>
            <div className="chat-title">
                {builtin ? (
                    <span>
                        <i className="fas fa-search" />
                        <b>LensQL builtin function</b>
                    </span>
                ) : (
                    <span>
                        <i className="fas fa-user" />
                        <b>User query</b>
                    </span>
                )}
                <pre>{query}</pre>
            </div>
            <hr />

            {message ? (
                <pre>{result}</pre>
            ) : (
                <div dangerouslySetInnerHTML={{ __html: result }} />
            )}

            {!builtin && (
                <Chat messages={messages} success={success} />
            )}
        </div>
    );
}

export default QueryResult;