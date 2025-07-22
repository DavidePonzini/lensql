import { useEffect, useState } from "react";
import AuthProvider from "../hooks/useAuth";
import ButtonModal from "./ButtonModal";

function ButtonShowDataset({ classId, footerButtons, className = 'btn btn-secondary', buttonText = 'Dataset', disabled = false, variant = 'secondary' }) {
    const { apiRequest } = AuthProvider();
    const [dataset, setDataset] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function fetchDataset() {
            setIsLoading(true);

            const response = await apiRequest(`/api/datasets/${classId}`, 'GET');

            if (!response.success) {
                alert(response.message);
                setIsLoading(false);
                return;
            }

            
            setDataset(response.data);
            setIsLoading(false);
        }

        fetchDataset();
    }, [classId, apiRequest]);

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