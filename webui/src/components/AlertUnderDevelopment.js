import { useTranslation } from 'react-i18next';

function AlertUnderDevelopment() {
    const { t } = useTranslation();

    return (
        <div className="alert alert-warning mt-4" role="alert">
            {t('components.alert.under_development')}
        </div>
    );
}

export default AlertUnderDevelopment;
