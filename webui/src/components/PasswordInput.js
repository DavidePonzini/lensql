import { useState } from 'react';
import { useTranslation } from 'react-i18next';

function PasswordInput({ error, className = '', ...props }) {
    const [visible, setVisible] = useState(false);
    const { t } = useTranslation();
    return (
        <div className="input-group">
            <input {...props} type={visible ? 'text' : 'password'}
                className={`form-control ${className} ${error ? 'is-invalid' : ''}`}
                aria-invalid={Boolean(error)}
                aria-describedby={error ? `${props.id}-error` : undefined} />
            <button type="button" className="input-group-text" disabled={props.disabled}
                onClick={() => setVisible(value => !value)} aria-controls={props.id}
                aria-pressed={visible} aria-label={t(visible ? 'pages.login.hide' : 'pages.login.show')}>
                <i className={`fas ${visible ? 'fa-eye-slash' : 'fa-eye'}`} aria-hidden="true" style={{ width: '1.5rem' }} />
            </button>
            {error && <div id={`${props.id}-error`} className="invalid-feedback">{error}</div>}
        </div>
    );
}

export default PasswordInput;
