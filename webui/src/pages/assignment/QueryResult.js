import Chat from './Chat';

import './QueryResult.css';

function QueryResult({ result, isBuiltin, queryId, query, success, isMessage, notices }) {
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
                <pre style={{maxHeight: '500px', overflow: 'auto'}}>{query}</pre>
            </div>
            <hr />

            {notices && notices.length > 0 && (
                <>
                    <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
                        {
                            notices.map((notice, index) => (
                                <li key={index} className='query-notice'>
                                    {notice.split('\n').map((line, i) => (
                                        <span key={i}>
                                            {line}
                                            <br />
                                        </span>
                                    ))}
                                </li>
                            ))
                        }
                    </ul>

                    <hr />
                </>
            )
            }

            {
                isMessage ? (
                    <pre>{result}</pre>
                ) : (
                    <div className='query-result' dangerouslySetInnerHTML={{ __html: result }} />
                )
            }

            {
                !isBuiltin && (
                    <Chat
                        key={queryId}
                        queryId={queryId}
                        success={success}
                    />
                )
            }
        </div >
    );
}

export default QueryResult;