import Chat from './Chat';

function QueryResult({ result, isBuiltin, queryId, query, success, isMessage }) {
    return (
        <div className={`chat alert ${isBuiltin ? 'alert-secondary' : success ? 'alert-primary' : 'alert-danger'}`}>
            <div className="chat-title">
                {isBuiltin ? (
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

            {isMessage ? (
                <pre>{result}</pre>
            ) : (
                <div dangerouslySetInnerHTML={{ __html: result }} />
            )}

            {!isBuiltin && (
                <Chat
                    queryId={queryId}
                    success={success}
                />
            )}
        </div>
    );
}

export default QueryResult;