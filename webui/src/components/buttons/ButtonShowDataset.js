import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import AuthProvider from "../../hooks/useAuth";

import ButtonModal from "./ButtonModal";

function ButtonShowDataset({ datasetId, footerButtons, className = 'btn btn-secondary', buttonText = null, disabled = false, variant = 'secondary' }) {
    const { t } = useTranslation();
    const { apiRequest } = AuthProvider();
    const [dataset, setDataset] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function fetchDataset() {
            setIsLoading(true);

            const response = await apiRequest(`/api/datasets/${datasetId}/str`, 'GET');

            if (!response.success) {
                alert(response.message);
                setIsLoading(false);
                return;
            }

            setDataset(response.data);
            setIsLoading(false);
        }

        fetchDataset();
    }, [datasetId, apiRequest]);

    return (
        <ButtonModal
            variant={variant}
            className={className}
            title={t('components.buttons.dataset.title')}
            buttonText={buttonText || t('components.buttons.dataset.title')}
            size="lg"
            footerButtons={footerButtons}
            disabled={disabled}
        >
            {isLoading ? (
                <p>{t('components.buttons.dataset.loading')}</p>
            ) : (
                <pre className="code" style={{
                    // userSelect: 'none',
                    maxHeight: '70vh',
                    overflow: 'auto'
                }}>
                    {dataset}
                </pre>
            )}
        </ButtonModal>
    );
}

export default ButtonShowDataset;
