import Chat from './Chat';

import '../styles/QueryResult.css';

function QueryResult({ result, isBuiltin, queryId, query, success, isMessage }) {
    return (
        <div className={`query-result alert ${success ? isBuiltin ? 'alert-secondary' : 'alert-primary' : 'alert-danger'}`}>
            <div className="query-result-title">
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
                    key={queryId}
                    queryId={queryId}
                    success={success}
                />
            )}
        </div>
    );
}

export default QueryResult;