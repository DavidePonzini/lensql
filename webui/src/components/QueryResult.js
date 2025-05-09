function QueryResult({ result, builtin, queryId, query, success, type }) {
    return (
        <div className={`chat alert ${builtin ? 'alert-secondary' : success ? 'alert-primary' : 'alert-danger'}`}>
            <div className="chat-title">
                <i className="fas fa-user" />
                <b>User query</b>
                <pre>{query}</pre>
            </div>
            <hr />
            {type === 'message' && (
                <pre>{result}</pre>
            )}
            {type === 'dataset' && (
                <div dangerouslySetInnerHTML={{ __html: result }} />
            )}
        </div>
    );
}

export default QueryResult;