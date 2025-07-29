import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import useAuth from '../hooks/useAuth';

import bg from '../res/database.jpg';

function Login() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { saveTokens } = useAuth();

    const [usernameInput, setUsernameInput] = useState('');
    const [usernameError, setUsernameError] = useState('');
    const [isUsernameValid, setIsUsernameValid] = useState(false);

    const [passwordInput, setPasswordInput] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [passwordError, setPasswordError] = useState('');
    const [isPasswordValid, setIsPasswordValid] = useState(false);

    const [error, setError] = useState('');

    function checkUsername(username) {
        setUsernameInput(username);

        if (!username) {
            setIsUsernameValid(false);
            setUsernameError(t('pages.login.usernameRequired'));
            return;
        }

        setIsUsernameValid(true);
        setUsernameError('');
    }

    function checkPassword(password) {
        setPasswordInput(password);

        if (!password) {
            setIsPasswordValid(false);
            setPasswordError(t('pages.login.passwordRequired'));
            return;
        }

        setIsPasswordValid(true);
        setPasswordError('');
    }

    async function handleLogin(event) {
        event.preventDefault();

        const hasUsername = usernameInput.trim();
        const hasPassword = passwordInput.trim();

        if (!hasUsername || !hasPassword) {
            setError(t('pages.login.errorEmptyFields'));
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: usernameInput, password: passwordInput })
            });

            const data = await response.json();

            if (data.success) {
                setError('');
                saveTokens(data.access_token, data.refresh_token);
                navigate('/');
            } else {
                setError(data.message || t('pages.login.errorLoginFailed'));
            }
        } catch (err) {
            setError(t('pages.login.errorServer'));
        }
    }

    return (
        <div className="container-md">
            <section>
                <div className="row g-0">
                    <div className="col-md-6 col-lg-5 d-none d-md-block" style={{
                        borderRadius: '1rem 0 0 1rem',
                        backgroundImage: `url(${bg})`,
                        backgroundAttachment: 'fixed',
                        backgroundPosition: 'center',
                        backgroundRepeat: 'no-repeat',
                        backgroundSize: 'cover',
                        position: 'sticky',
                        zIndex: 100,
                    }}></div>

                    <div className="col-md-6 col-lg-7 d-flex align-items-center">
                        <div className="card-body p-4 p-lg-5 text-black">
                            <form onSubmit={handleLogin} noValidate>
                                <div className="d-flex align-items-center mb-3 pb-1">
                                    <i className="fas fa-search fa-2x me-3" style={{ color: 'var(--logo-color)' }} />
                                    <span className="h1 fw-bold mb-0">LensQL</span>
                                </div>

                                <h5 className="fw-normal mb-1" style={{ letterSpacing: 1 }}>{t('pages.login.title')}</h5>

                                <Link to="/register" className="text-muted mb-4 d-block">
                                    {t('pages.login.subtitle')}
                                </Link>

                                {error && (
                                    <div className="alert alert-danger" role="alert">
                                        {error}
                                    </div>
                                )}

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-username">
                                        {t('pages.login.username')}
                                    </label>
                                    <input
                                        type="text"
                                        id="login-username"
                                        className={`form-control form-control-lg ${usernameError ? 'is-invalid' : ''}`}
                                        placeholder={t('pages.login.usernamePlaceholder')}
                                        value={usernameInput}
                                        onInput={(e) => checkUsername(e.target.value)}
                                        autoFocus
                                    />
                                    {usernameError && (
                                        <div className="invalid-feedback">
                                            {usernameError}
                                        </div>
                                    )}
                                </div>

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-password">
                                        {t('pages.login.password')}
                                    </label>

                                    <div className="input-group">
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            id="login-password"
                                            className={`form-control form-control-lg pe-5 ${passwordError ? 'is-invalid' : ''}`}
                                            placeholder={t('pages.login.passwordPlaceholder')}
                                            value={passwordInput}
                                            onInput={(e) => checkPassword(e.target.value)}
                                        />
                                        <div className="input-group-text" style={{ cursor: 'pointer' }}>
                                            <i
                                                className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}
                                                onClick={() => setShowPassword(!showPassword)}
                                                aria-label={showPassword ? t('pages.login.hide') : t('pages.login.show')}
                                                style={{ width: '1.5rem' }}
                                            ></i>
                                        </div>
                                        {passwordError && (
                                            <div className="invalid-feedback">
                                                {passwordError}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="pt-1 mb-4">
                                    <button
                                        className="btn btn-primary btn-lg btn-block w-100"
                                        type="submit"
                                        disabled={!isUsernameValid || !isPasswordValid}
                                    >
                                        {t('pages.login.submit')}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Login;
