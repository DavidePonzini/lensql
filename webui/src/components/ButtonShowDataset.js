import { useEffect, useState } from "react";
import AuthProvider from "../hooks/useAuth";
import ButtonModal from "./ButtonModal";

function ButtonShowDataset({ datasetId, footerButtons, className = 'btn btn-secondary', buttonText = 'Dataset' }) {
    const { apiRequest } = AuthProvider();
    const [dataset, setDataset] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function fetchDataset() {
            setIsLoading(true);
            try {
                const response = await apiRequest(`/api/get-dataset?id=${datasetId ? datasetId : ''}`);
                setDataset(response.data);
            } catch (error) {
                console.error('Error fetching dataset:', error);
            } finally {
                setIsLoading(false);
            }
        }

        fetchDataset();
    }, [datasetId, apiRequest]);

    return (
        <ButtonModal
            className={className}
            title="Dataset"
            buttonText={buttonText}
            size="lg"
            footerButtons={footerButtons}
        >
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <pre className="code" style={{ userSelect: 'none' }}>
                    {dataset}
                </pre>
            )}
        </ButtonModal>

    )
}

export default ButtonShowDataset;