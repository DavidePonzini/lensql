import ButtonAction from "../../components/ButtonAction";
import ButtonCategory from "./ButtonCategory";
import ButtonActionDropdown from "../../components/ButtonActionDropdown";
import useAuth from "../../hooks/useAuth";

function ButtonsDatabase({ exerciseId, isExecuting, setIsExecuting, setResult }) {
    const { apiRequest } = useAuth();

    async function handleShowSearchPath() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/show-search-path', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    async function handleListSchemas() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-schemas', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    async function handleListTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    async function handleListAllTables() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-all-tables', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    async function handleListConstraints() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/builtin/list-constraints', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    return (
        <>
            <ButtonCategory
                text="Database"
                iconClassName='fas fa-database'
                className="text-secondary"
            />
            <div className="col">

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleShowSearchPath}
                    disabled={isExecuting}
                >
                    Show Search Path
                </ButtonAction>

                <ButtonActionDropdown
                    title="List Tables"
                    disabled={isExecuting}
                    variant="secondary"
                    className="me-1 mb-1"
                    buttons={[
                        {
                            label: 'Current Schema',
                            onClick: handleListTables,
                            disabled: isExecuting,
                        },
                        {
                            label: 'All Schemas',
                            onClick: handleListAllTables,
                            disabled: isExecuting,
                        },
                    ]}
                />

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleListSchemas}
                    disabled={isExecuting}
                >
                    List Schemas
                </ButtonAction>

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleListConstraints}
                    disabled={isExecuting}
                >
                    List Constraints
                </ButtonAction>
            </div>
        </>
    );
}

export default ButtonsDatabase;