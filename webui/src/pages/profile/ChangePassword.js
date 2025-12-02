import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from '../../hooks/useAuth';

function ChangePassword() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();

    // Current password
    const [currentPassword, setCurrentPassword] = useState('');
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);
    const [currentPasswordError, setCurrentPasswordError] = useState('');
    const [isCurrentValid, setIsCurrentValid] = useState(false);

    // New password
    const [newPassword, setNewPassword] = useState('');
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [newPasswordError, setNewPasswordError] = useState('');
    const [isNewValid, setIsNewValid] = useState(false);

    // Confirm password
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [confirmPasswordError, setConfirmPasswordError] = useState('');
    const [isConfirmValid, setIsConfirmValid] = useState(false);

    // Result messages
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    // -----------------------------------------------------
    // Validation
    // -----------------------------------------------------
    function checkCurrentPassword(value) {
        setCurrentPassword(value);

        if (!value) {
            setCurrentPasswordError(t('pages.profile.profile.change_password.current_required'));
            setIsCurrentValid(false);
            return false;
        }
        setCurrentPasswordError('');
        setIsCurrentValid(true);
        return true;
    }

    function checkNewPassword(password) {
        setNewPassword(password);

        if (!password) return invalidate(t('pages.register.passwordRequired'));
        if (password.length < 8) return invalidate(t('pages.register.passwordLength'));
        if (!/[A-Z]/.test(password)) return invalidate(t('pages.register.passwordUpper'));
        if (!/[a-z]/.test(password)) return invalidate(t('pages.register.passwordLower'));
        if (!/[0-9]/.test(password)) return invalidate(t('pages.register.passwordDigit'));
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password))
            return invalidate(t('pages.register.passwordSpecial'));

        setIsNewValid(true);
        setNewPasswordError('');

        checkConfirmPassword(confirmPassword, password);
        return true;

        function invalidate(msg) {
            setIsNewValid(false);
            setNewPasswordError(msg);
            setIsConfirmValid(false);
            return false;
        }
    }

    function checkConfirmPassword(value, main = newPassword) {
        setConfirmPassword(value);

        if (!value) {
            setConfirmPasswordError(
                t('pages.profile.profile.change_password.confirm_required')
            );
            setIsConfirmValid(false);
            return false;
        }

        if (value !== main) {
            setConfirmPasswordError(
                t('pages.profile.profile.change_password.password_mismatch_alert')
            );
            setIsConfirmValid(false);
            return false;
        }

        setConfirmPasswordError('');
        setIsConfirmValid(true);
        return true;
    }

    const isFormValid =
        isCurrentValid && isNewValid && isConfirmValid;

    // -----------------------------------------------------
    // Submit
    // -----------------------------------------------------
    async function handleSubmit(event) {
        event.preventDefault();

        try {
            const response = await apiRequest('api/auth/change-password', 'POST', {
                old_password: currentPassword,
                new_password: newPassword,
            });

            if (response.success) {
                setError('');
                setSuccess(true);

                // Clear fields
                setCurrentPassword('');
                setNewPassword('');
                setConfirmPassword('');
                setIsCurrentValid(false);
                setIsNewValid(false);
                setIsConfirmValid(false);
            } else {
                setSuccess(false);
                setError(
                    response.message ||
                        t('pages.profile.profile.change_password.error_generic')
                );
            }
        } catch {
            setSuccess(false);
            setError(
                t('pages.profile.profile.change_password.error_generic')
            );
        }
    }

    // -----------------------------------------------------
    // Render
    // -----------------------------------------------------
    return (
        <div className="card p-4">
            <h4 className="mb-3">
                {t('pages.profile.profile.change_password.title')}
            </h4>

            {error && <div className="alert alert-danger">{error}</div>}
            {success && (
                <div className="alert alert-success">
                    {t('pages.profile.profile.change_password.success_alert')}
                </div>
            )}

            <form onSubmit={handleSubmit} noValidate>

                {/* Current password */}
                <div className="form-outline mb-4">
                    <label className="form-label" htmlFor="current-password">
                        {t('pages.profile.profile.change_password.current_password_label')}
                    </label>

                    <div className="input-group">
                        <input
                            type={showCurrentPassword ? 'text' : 'password'}
                            id="current-password"
                            className={`form-control form-control-lg pe-5 ${
                                currentPasswordError ? 'is-invalid' : ''
                            }`}
                            value={currentPassword}
                            onInput={(e) => checkCurrentPassword(e.target.value)}
                        />
                        <div
                            className="input-group-text"
                            style={{ cursor: 'pointer' }}
                            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        >
                            <i
                                className={`fas ${
                                    showCurrentPassword ? 'fa-eye-slash' : 'fa-eye'
                                }`}
                            />
                        </div>

                        {currentPasswordError && (
                            <div className="invalid-feedback">{currentPasswordError}</div>
                        )}
                    </div>
                </div>

                {/* New password */}
                <div className="form-outline mb-4">
                    <label className="form-label" htmlFor="new-password">
                        {t('pages.profile.profile.change_password.new_password_label')}
                    </label>

                    <div className="input-group">
                        <input
                            type={showNewPassword ? 'text' : 'password'}
                            id="new-password"
                            className={`form-control form-control-lg pe-5 ${
                                newPasswordError ? 'is-invalid' : ''
                            }`}
                            value={newPassword}
                            onInput={(e) => checkNewPassword(e.target.value)}
                        />
                        <div
                            className="input-group-text"
                            style={{ cursor: 'pointer' }}
                            onClick={() => setShowNewPassword(!showNewPassword)}
                        >
                            <i
                                className={`fas ${
                                    showNewPassword ? 'fa-eye-slash' : 'fa-eye'
                                }`}
                            />
                        </div>

                        {newPasswordError && (
                            <div className="invalid-feedback">{newPasswordError}</div>
                        )}
                    </div>
                </div>

                {/* Confirm password */}
                <div className="form-outline mb-4">
                    <label className="form-label" htmlFor="confirm-password">
                        {t('pages.profile.profile.change_password.confirm_new_password_label')}
                    </label>

                    <div className="input-group">
                        <input
                            type={showConfirmPassword ? 'text' : 'password'}
                            id="confirm-password"
                            className={`form-control form-control-lg pe-5 ${
                                confirmPasswordError ? 'is-invalid' : ''
                            }`}
                            value={confirmPassword}
                            onInput={(e) => checkConfirmPassword(e.target.value)}
                        />
                        <div
                            className="input-group-text"
                            style={{ cursor: 'pointer' }}
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        >
                            <i
                                className={`fas ${
                                    showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'
                                }`}
                            />
                        </div>

                        {confirmPasswordError && (
                            <div className="invalid-feedback">
                                {confirmPasswordError}
                            </div>
                        )}
                    </div>
                </div>

                {/* Submit */}
                <div className="pt-1 mb-2">
                    <button
                        className="btn btn-primary btn-lg w-100"
                        type="submit"
                        disabled={!isFormValid}
                    >
                        {t('pages.profile.profile.change_password.submit_button')}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default ChangePassword;
