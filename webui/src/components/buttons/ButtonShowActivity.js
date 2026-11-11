import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import AuthProvider from "../../hooks/useAuth";

import ButtonModal from "./ButtonModal";

function ButtonShowActivity({ activityId, footerButtons, className = 'btn btn-secondary', buttonText = null, disabled = false, variant = 'secondary' }) {
    const { t } = useTranslation();
    const { apiRequest } = AuthProvider();
    const [activity, setActivity] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function fetchActivity() {
            setIsLoading(true);

            const response = await apiRequest(`/api/activities/${activityId}/str`, 'GET');

            if (!response.success) {
                alert(response.message);
                setIsLoading(false);
                return;
            }

            setActivity(response.data);
            setIsLoading(false);
        }

        fetchActivity();
    }, [activityId, apiRequest]);

    return (
        <ButtonModal
            variant={variant}
            className={className}
            title={t('components.buttons.activity.title')}
            buttonText={buttonText || t('components.buttons.activity.title')}
            size="lg"
            footerButtons={footerButtons}
            disabled={disabled}
        >
            {isLoading ? (
                <p>{t('components.buttons.activity.loading')}</p>
            ) : (
                <pre className="code" style={{
                    // userSelect: 'none',
                    maxHeight: '70vh',
                    overflow: 'auto'
                }}>
                    {activity}
                </pre>
            )}
        </ButtonModal>
    );
}

export default ButtonShowActivity;
