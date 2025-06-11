import { useEffect, useState } from "react";
import AuthProvider from "../hooks/useAuth";
import ButtonModal from "./ButtonModal";

function ButtonShowDataset({ datasetName, footerButtons, className = 'btn btn-secondary', buttonText = 'Dataset', disabled = false, variant = 'secondary' }) {
    const { apiRequest } = AuthProvider();
    const [dataset, setDataset] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function fetchDataset() {
            setIsLoading(true);
            try {
                const response = await apiRequest(`/api/datasets/?name=${datasetName ? datasetName : ''}`, 'GET');
                setDataset(response.data);
            } catch (error) {
                console.error('Error fetching dataset:', error);
            } finally {
                setIsLoading(false);
            }
        }

        fetchDataset();
    }, [datasetName, apiRequest]);

    return (
        <ButtonModal
            variant={variant}
            className={className}
            title="Dataset"
            buttonText={buttonText}
            size="lg"
            footerButtons={footerButtons}
            disabled={disabled}
        >
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <pre className="code" style={{ userSelect: 'none', maxHeight: '70vh', overflow: 'auto' }}>
                    {dataset}
                </pre>
            )}
        </ButtonModal>

    )
}

export default ButtonShowDataset;