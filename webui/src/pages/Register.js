import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import bg from '../res/database.jpg';

function Register() {
    const { t, i18n } = useTranslation();

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
            setUsernameError(t('pages.register.usernameRequired'));
            return false;
        }
        setIsUsernameValid(true);
        setUsernameError('');
        return true;
    }

    function checkPassword(password) {
        setPasswordInput(password);

        if (!password) return invalidate(t('pages.register.passwordRequired'));
        if (password.length < 8) return invalidate(t('pages.register.passwordLength'));
        if (!/[A-Z]/.test(password)) return invalidate(t('pages.register.passwordUpper'));
        if (!/[a-z]/.test(password)) return invalidate(t('pages.register.passwordLower'));
        if (!/[0-9]/.test(password)) return invalidate(t('pages.register.passwordDigit'));
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return invalidate(t('pages.register.passwordSpecial'));

        setIsPasswordValid(true);
        setPasswordError('');
        return true;

        function invalidate(msg) {
            setIsPasswordValid(false);
            setPasswordError(msg);
            return false;
        }
    }

    function checkEmail(email) {
        setEmailInput(email);
        if (!email) return valid(); // Optional
        if (!email.match(/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/)) {
            setIsEmailValid(false);
            setEmailError(t('pages.register.emailInvalid'));
            return false;
        }
        return valid();

        function valid() {
            setIsEmailValid(true);
            setEmailError('');
            return true;
        }
    }

    function checkSchool(school) {
        setSchoolInput(school);
        if (!school) {
            setIsSchoolValid(false);
            setSchoolError(t('pages.register.schoolRequired'));
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
                    'Content-Type': 'application/json',
                    'X-Language': i18n.language || 'en', // Use the current language from i18n
                },
                body: JSON.stringify({
                    username: usernameInput,
                    password: passwordInput,
                    email: emailInput,
                    school: schoolInput,
                })
            });

            const data = await response.json();
            if (data.success) {
                setError('');
                setSuccess(true);
            } else {
                setError(data.message || t('pages.register.errorGeneric'));
            }
        } catch {
            setError(t('pages.register.errorServer'));
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
                            <form onSubmit={handleRegister} noValidate>
                                <div className="d-flex align-items-center mb-3 pb-1">
                                    <i className="fas fa-search fa-2x me-3" style={{ color: 'var(--logo-color)' }} />
                                    <span className="h1 fw-bold mb-0">LensQL</span>
                                </div>

                                <h5 className="fw-normal mb-1">{t('pages.register.title')}</h5>

                                <Link to="/login" className="text-muted mb-4 d-block">
                                    {t('pages.register.subtitle')}
                                </Link>

                                {error && (
                                    <div className="alert alert-danger" role="alert">
                                        {error}
                                    </div>
                                )}

                                {success && (
                                    <div className="alert alert-success" role="alert">
                                        {t('pages.register.success')}
                                        <br />
                                        <Link to="/login" className="alert-link">{t('pages.register.gotoLogin')}</Link>
                                    </div>
                                )}

                                {/* Username */}
                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="register-username">
                                        {t('pages.register.username')}
                                    </label>
                                    <input
                                        type="text"
                                        id="register-username"
                                        className={`form-control form-control-lg ${usernameError ? 'is-invalid' : ''}`}
                                        placeholder={t('pages.register.usernamePlaceholder')}
                                        value={usernameInput}
                                        onInput={(e) => checkUsername(e.target.value)}
                                        autoFocus
                                    />
                                    {usernameError && <div className="invalid-feedback">{usernameError}</div>}
                                </div>

                                {/* Password */}
                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="register-password">
                                        {t('pages.register.password')}
                                    </label>
                                    <div className="input-group">
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            id="register-password"
                                            className={`form-control form-control-lg pe-5 ${passwordError ? 'is-invalid' : ''}`}
                                            placeholder={t('pages.register.passwordPlaceholder')}
                                            value={passwordInput}
                                            onInput={(e) => checkPassword(e.target.value)}
                                        />
                                        <div className="input-group-text" style={{ cursor: 'pointer' }}>
                                            <i
                                                className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}
                                                onClick={() => setShowPassword(!showPassword)}
                                                aria-label={showPassword ? t('pages.register.hide') : t('pages.register.show')}
                                            />
                                        </div>
                                        {passwordError && <div className="invalid-feedback">{passwordError}</div>}
                                    </div>
                                </div>

                                {/* Email */}
                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="register-email">
                                        {t('pages.register.email')}
                                    </label>
                                    <input
                                        type="email"
                                        id="register-email"
                                        className={`form-control form-control-lg ${emailError ? 'is-invalid' : ''}`}
                                        placeholder={t('pages.register.emailPlaceholder')}
                                        value={emailInput}
                                        onInput={(e) => checkEmail(e.target.value)}
                                    />
                                    {emailError && <div className="invalid-feedback">{emailError}</div>}
                                </div>

                                {/* School */}
                                <div className="form-outline mb-4">
                                    <label className="form-label" htmlFor="register-school">
                                        {t('pages.register.school')}
                                    </label>
                                    <input
                                        type="text"
                                        id="register-school"
                                        className={`form-control form-control-lg ${schoolError ? 'is-invalid' : ''}`}
                                        placeholder={t('pages.register.schoolPlaceholder')}
                                        value={schoolInput}
                                        onInput={(e) => checkSchool(e.target.value)}
                                    />
                                    {schoolError && <div className="invalid-feedback">{schoolError}</div>}
                                </div>

                                {/* Submit */}
                                <div className="pt-1 mb-4">
                                    <button
                                        className="btn btn-primary btn-lg btn-block w-100"
                                        type="submit"
                                        disabled={
                                            !isUsernameValid || !isPasswordValid || !isEmailValid || !isSchoolValid
                                        }
                                    >
                                        {t('pages.register.submit')}
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
