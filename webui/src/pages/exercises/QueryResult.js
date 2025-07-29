import { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';

import Chat from './Chat';

import './QueryResult.css';

const QueryResult = forwardRef(({ result, isBuiltin, queryId, query, success, isMessage, notices }, ref) => {
    const { t } = useTranslation();
    
    return (
        <div
            className={`query-result alert ${success ? isBuiltin ? 'alert-secondary' : 'alert-primary' : 'alert-danger'}`}
            ref={ref}
        >
            <div className="query-result-title">
                {isBuiltin ? (
                    <span>
                        <i className="fas fa-search" />
                        <b>{t('pages.exercises.query_result.builtin')}</b>
                    </span>
                ) : (
                    <span>
                        <i className="fas fa-user" />
                        <b>{t('pages.exercises.query_result.user')}</b>
                    </span>
                )}
                <pre style={{ maxHeight: '500px', overflow: 'auto' }}>{query}</pre>
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
                    <div dangerouslySetInnerHTML={{ __html: result }} />
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
});

export default QueryResult;