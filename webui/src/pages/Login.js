import { useState } from 'react';
import useAuth from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

import bg from '../res/database.jpg';

function Login() {
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
            setUsernameError('Please enter a username.');
            return;
        }

        setIsUsernameValid(true);
        setUsernameError('');
        return true;
    }

    function checkPassword(password) {
        setPasswordInput(password);

        if (!password) {
            setIsPasswordValid(false);
            setPasswordError('Please enter a password.');
            return;
        }

        setIsPasswordValid(true);
        setPasswordError('');
        return true;
    }

    async function handleLogin(event) {
        event.preventDefault();

        const hasUsername = usernameInput.trim();
        const hasPassword = passwordInput.trim();

        if (!hasUsername || !hasPassword) {
            setError('Please fill in both fields.');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: usernameInput, password: passwordInput })
            });

            const data = await response.json();

            if (data.success) {
                setError('');
                saveTokens(data.access_token, data.refresh_token);
                navigate('/');
            } else {
                setError(data.message || 'Login failed');
            }
        } catch (error) {
            setError('Could not connect to the server.');
        }
    }

    return (
        <div className='container-md'>
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
                                <h5 className="fw-normal mb-3 pb-3" style={{ letterSpacing: 1 }}>Sign into your account</h5>

                                {error && (
                                    <div className="alert alert-danger" role="alert">
                                        {error}
                                    </div>
                                )}

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-username">
                                        Username
                                    </label>
                                    <input
                                        type="text"
                                        id="login-username"
                                        className={`form-control form-control-lg ${usernameError ? 'is-invalid' : ''}`}
                                        placeholder="Username"
                                        value={usernameInput}
                                        onInput={(e) => checkUsername(e.target.value)}
                                        autoFocus={true}
                                    />
                                    {usernameError && (
                                        <div className="invalid-feedback">
                                            {usernameError}
                                        </div>
                                    )}
                                </div>

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-password">
                                        Password
                                    </label>

                                    <div className="input-group">
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            id="login-password"
                                            className={`form-control form-control-lg pe-5 ${passwordError ? 'is-invalid' : ''}`}
                                            placeholder="Password"
                                            value={passwordInput}
                                            onInput={(e) => checkPassword(e.target.value)}
                                        />
                                        <div
                                            className="input-group-text"
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <i
                                                className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}
                                                onClick={() => setShowPassword(!showPassword)}
                                                aria-label={showPassword ? 'Hide password' : 'Show password'}
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
                                        onClick={handleLogin}
                                        disabled={!isUsernameValid || !isPasswordValid}
                                    >
                                        Login
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
