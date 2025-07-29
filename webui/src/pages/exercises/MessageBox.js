import { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';

import Message from './Message';

import './MessageBox.css';

const MessageBox = forwardRef(({ children, text, assistant = false, thinking = false, messageId = null }, ref) => {
    const { t } = useTranslation();

    return (
        <div
            className={`messagebox ${assistant ? 'messagebox-assistant' : 'messagebox-user'} ${thinking ? 'thinking' : ''}`}
            ref={ref}
        >
            {assistant && (
                <div className="icon">
                    <i className="fas fa-search" />
                    <br />
                    {t('pages.exercises.messageBox.assistant_name')}
                </div>
            )}

            <Message messageId={messageId} text={text}>
                {children}
            </Message>

            {!assistant && (
                <div className="icon">
                    <i className="fas fa-user" />
                    <br />
                    {t('pages.exercises.messageBox.user_name')}
                </div>
            )}
        </div>
    );
});

export default MessageBox;