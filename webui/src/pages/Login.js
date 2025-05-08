import React, { useState } from 'react';
import '../styles/Login.css';
import Button from '../components/Button';
import Footer from '../components/Footer';

function Login({ setToken }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');

    async function handleLogin(event) {
        event.preventDefault();

        const hasUsername = username.trim();
        const hasPassword = password.trim();

        if (!hasUsername || !hasPassword) {
            setError('Please fill in both fields.');
            return;
        }

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                setError('');
                setToken(data.token);
            } else {
                setError(data.message || 'Login failed');
            }
        } catch (error) {
            setError('Could not connect to the server.');
        }
    }

    return (
        <section className="login vh-100">
            <div className="container py-5 h-100">
                <div className="row d-flex justify-content-center align-items-center h-100">
                    <div className="col col-xl-10">
                        <div className="card">
                            <div className="row g-0">
                                <div className="col-md-6 col-lg-5 d-none d-md-block img"></div>
                                <div className="col-md-6 col-lg-7 d-flex align-items-center">
                                    <div className="card-body p-4 p-lg-5 text-black">
                                        <form onSubmit={handleLogin} noValidate>
                                            <div className="d-flex align-items-center mb-3 pb-1">
                                                <i className="fas fa-search fa-2x me-3 logo" />
                                                <span className="h1 fw-bold mb-0">LensQL</span>
                                            </div>
                                            <h5 className="fw-normal mb-3 pb-3">Sign into your account</h5>

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
                                                    className="form-control form-control-lg"
                                                    placeholder="Username"
                                                    value={username}
                                                    onInput={(e) => {
                                                        setUsername(e.target.value);
                                                    }}
                                                />
                                            </div>

                                            <div className="form-outline mb-4">
                                                <label className="form-label" htmlFor="login-password">
                                                    Password
                                                </label>

                                                <div className="input-group">
                                                    <input
                                                        type={showPassword ? 'text' : 'password'}
                                                        id="login-password"
                                                        className="form-control form-control-lg pe-5"
                                                        placeholder="Password"
                                                        value={password}
                                                        onChange={(e) => setPassword(e.target.value)}
                                                    />
                                                    <div className="input-group-text show-password">
                                                        <i
                                                            className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}
                                                            onClick={() => setShowPassword(!showPassword)}
                                                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                                                        ></i>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="pt-1 mb-4">
                                                <Button
                                                    className="btn-primary btn-lg btn-block w-100"
                                                    onClick={handleLogin}
                                                >
                                                    Login
                                                </Button>
                                            </div>
                                        </form>

                                        <hr></hr>
                                        <Footer />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default Login;
