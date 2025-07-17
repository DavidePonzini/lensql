import { useState } from 'react';
import { Link } from 'react-router-dom';

import bg from '../res/database.jpg';

function Register() {
    const [usernameInput, setUsernameInput] = useState('');
    const [usernameError, setUsernameError] = useState('');
    const [isUsernameValid, setIsUsernameValid] = useState(false);

    const [passwordInput, setPasswordInput] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [passwordError, setPasswordError] = useState('');
    const [isPasswordValid, setIsPasswordValid] = useState(false);

    const [emailInput, setEmailInput] = useState('');
    const [emailError, setEmailError] = useState('');
    const [isEmailValid, setIsEmailValid] = useState(false);

    const [schoolInput, setSchoolInput] = useState('');
    const [schoolError, setSchoolError] = useState('');
    const [isSchoolValid, setIsSchoolValid] = useState(false);

    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    function checkUsername(username) {
        setUsernameInput(username);

        if (!username) {
            setIsUsernameValid(false);
            setUsernameError('Please enter a username.');
            return false;
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
            return false;
        }

        if (password.length < 8) {
            setIsPasswordValid(false);
            setPasswordError('Password must be at least 8 characters long.');
            return false;
        }

        if (!/[A-Z]/.test(password)) {
            setIsPasswordValid(false);
            setPasswordError('Password must contain at least one uppercase letter.');
            return false;
        }

        if (!/[a-z]/.test(password)) {
            setIsPasswordValid(false);
            setPasswordError('Password must contain at least one lowercase letter.');
            return false;
        }

        if (!/[0-9]/.test(password)) {
            setIsPasswordValid(false);
            setPasswordError('Password must contain at least one number.');
            return false;
        }

        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            setIsPasswordValid(false);
            setPasswordError('Password must contain at least one special character.');
            return false;
        }

        setIsPasswordValid(true);
        setPasswordError('');
        return true;
    }

    function checkEmail(email) {
        setEmailInput(email);

        if (!email) {
            setIsEmailValid(false);
            setEmailError('Please enter an email address.');
            return false;
        }

        if (!email.match(/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/)) {
            setIsEmailValid(false);
            setEmailError('Please enter a valid email address.');
            return false;
        }

        setIsEmailValid(true);
        setEmailError('');
        return true;
    }

    function checkSchool(school) {
        setSchoolInput(school);

        if (!school) {
            setIsSchoolValid(false);
            setSchoolError('Please enter your school.');
            return false;
        }

        setIsSchoolValid(true);
        setSchoolError('');
        return true;
    }

    async function handleRegister(event) {
        event.preventDefault();

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: usernameInput,
                    password: passwordInput,
                    email: emailInput,
                    school: schoolInput,
                })
            });

            const data = await response.json();
            console.log(data);

            if (data.success) {
                setError('');
                setSuccess(true);
            } else {
                setError(data.message || 'Registration failed');
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
                            <form onSubmit={handleRegister} noValidate>
                                <div className="d-flex align-items-center mb-3 pb-1">
                                    <i className="fas fa-search fa-2x me-3" style={{ color: 'var(--logo-color)' }} />
                                    <span className="h1 fw-bold mb-0">LensQL</span>
                                </div>
                                <h5 className="fw-normal mb-1" style={{ letterSpacing: 1 }}>Register a new account</h5>

                                <Link to="/login" className="text-muted mb-4 d-block">
                                    Already have an account? Log in here
                                </Link>

                                {error && (
                                    <div className="alert alert-danger" role="alert">
                                        {error}
                                    </div>
                                )}

                                {success && (
                                    <div className="alert alert-success" role="alert">
                                        Registration successful! You can now log in with your new account.
                                        <br />
                                        <Link to="/login" className="alert-link">Go to Login</Link>
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
                                            className='input-group-text'
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

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-email">
                                        Email
                                    </label>
                                    <input
                                        type="email"
                                        id="login-email"
                                        className={`form-control form-control-lg ${emailError ? 'is-invalid' : ''}`}
                                        placeholder="Email"
                                        value={emailInput}
                                        onInput={(e) => checkEmail(e.target.value)}
                                    />
                                    {emailError && (
                                        <div className="invalid-feedback">
                                            {emailError}
                                        </div>
                                    )}
                                </div>

                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="login-school">
                                        School
                                    </label>
                                    <input
                                        type="text"
                                        id="login-school"
                                        className={`form-control form-control-lg ${schoolError ? 'is-invalid' : ''}`}
                                        placeholder="School"
                                        value={schoolInput}
                                        onInput={(e) => checkSchool(e.target.value)}
                                    />
                                    {schoolError && (
                                        <div className="invalid-feedback">
                                            {schoolError}
                                        </div>
                                    )}
                                </div>

                                <div className="pt-1 mb-4">
                                    <button
                                        className="btn btn-primary btn-lg btn-block w-100"
                                        onClick={handleRegister}
                                        disabled={
                                            !isUsernameValid ||
                                            !isPasswordValid ||
                                            !isEmailValid ||
                                            !isSchoolValid
                                        }
                                    >
                                        Register
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

export default Register;

