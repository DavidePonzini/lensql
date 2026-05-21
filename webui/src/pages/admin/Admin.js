import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from '../../hooks/useAuth';
import useUserInfo from '../../hooks/useUserInfo';

function Admin() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { userInfo } = useUserInfo();
    const [formData, setFormData] = useState({ dataset_id: '', username: '', is_owner: false });
    const [message, setMessage] = useState({ type: '', text: '' });
    const [isLoading, setIsLoading] = useState(false);

    const isAdmin = userInfo?.isAdmin || false;

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });

        if (!isAdmin) {
            setMessage({ type: 'danger', text: t('pages.admin.add_user.error_admin') });
            return;
        }

        if (!formData.dataset_id.trim() || !formData.username.trim()) {
            setMessage({ type: 'danger', text: 'Please fill in all fields' });
            return;
        }

        setIsLoading(true);
        try {
            const response = await apiRequest('/api/datasets/add-user', 'POST', {
                dataset_id: formData.dataset_id.trim(),
                username: formData.username.trim(),
                is_owner: formData.is_owner
            });

            if (response.success) {
                setMessage({ type: 'success', text: t('pages.admin.add_user.success') });
            } else {
                const errorMessage = response.message || t('pages.admin.add_user.error_general');
                setMessage({ type: 'danger', text: errorMessage });
            }
        } catch (error) {
            let errorText = t('pages.admin.add_user.error_general');
            if (error.message.includes('does not exist')) {
                errorText = t('pages.admin.add_user.error_dataset');
            } else if (error.message.includes('User does not exist')) {
                errorText = t('pages.admin.add_user.error_user');
            }
            setMessage({ type: 'danger', text: errorText });
        } finally {
            setIsLoading(false);
        }
    };

    if (!isAdmin) {
        return (
            <div className="container-md">
                <h1>{t('pages.admin.title')}</h1>
                <div className="alert alert-warning">
                    <strong>⚠️ {t('pages.admin.add_user.error_admin')}</strong>
                </div>
            </div>
        );
    }

    return (
        <div className="container-md">
            <h1>{t('pages.admin.title')}</h1>

            <hr className="my-4" />

            <h2>{t('pages.admin.add_user.title')}</h2>

            {message.text && (
                <div className={`alert alert-${message.type} alert-dismissible fade show`} role="alert">
                    {message.text}
                    <button type="button" className="btn-close" onClick={() => setMessage({ type: '', text: '' })}></button>
                </div>
            )}

            <form onSubmit={handleSubmit} className="row g-3">
                <div className="col-md-6">
                    <label htmlFor="dataset_id" className="form-label">{t('pages.admin.add_user.dataset_label')}</label>
                    <input
                        type="text"
                        className="form-control"
                        id="dataset_id"
                        name="dataset_id"
                        placeholder={t('pages.admin.add_user.dataset_placeholder')}
                        value={formData.dataset_id}
                        onChange={handleInputChange}
                        disabled={isLoading}
                        required
                    />
                </div>

                <div className="col-md-6">
                    <label htmlFor="username" className="form-label">{t('pages.admin.add_user.username_label')}</label>
                    <input
                        type="text"
                        className="form-control"
                        id="username"
                        name="username"
                        placeholder={t('pages.admin.add_user.username_placeholder')}
                        value={formData.username}
                        onChange={handleInputChange}
                        disabled={isLoading}
                        required
                    />
                </div>

                <div className="col-12">
                    <div className="form-check">
                        <input
                            type="checkbox"
                            className="form-check-input"
                            id="is_owner"
                            name="is_owner"
                            checked={formData.is_owner}
                            onChange={handleInputChange}
                            disabled={isLoading}
                        />
                        <label className="form-check-label" htmlFor="is_owner">
                            {t('pages.admin.add_user.is_owner_label')}
                        </label>
                    </div>
                </div>

                <div className="col-12">
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2"></span>
                                {t('pages.admin.add_user.submit')}
                            </>
                        ) : (
                            t('pages.admin.add_user.submit')
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default Admin;
