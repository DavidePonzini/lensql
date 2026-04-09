import { useTranslation } from "react-i18next";

import useAuth from "../../hooks/useAuth";

import ButtonAction from "../../components/buttons/ButtonAction";
import ButtonActionDropdown from "../../components/buttons/ButtonActionDropdown";

import ButtonCategory from "./ButtonCategory";

function ButtonsDatabase({ exerciseId, isExecuting, setIsExecuting, setResult }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();

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

    async function handleDescribeTables() {
        setIsExecuting(true);
        const data = await apiRequest('/api/queries/builtin/describe-tables', 'POST', {
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

    async function handleListUsers() {
        setIsExecuting(true);
        const data = await apiRequest('/api/queries/builtin/list-users', 'POST', {
            'exercise_id': exerciseId,
        });
        setIsExecuting(false);
        setResult(data);
    }

    return (
        <>
            <ButtonCategory
                text={t('pages.exercises.buttons.category.database')}
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
                    {t('pages.exercises.buttons.database.show_search_path')}
                </ButtonAction>

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleListSchemas}
                    disabled={isExecuting}
                >
                    {t('pages.exercises.buttons.database.list_schemas')}
                </ButtonAction>

                <ButtonAction
                    disabled={isExecuting}
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleListTables}
                >
                    {t('pages.exercises.buttons.database.list_tables')}
                </ButtonAction>

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleDescribeTables}
                    disabled={isExecuting}
                >
                    {t('pages.exercises.buttons.database.describe_tables')}
                </ButtonAction>

                <ButtonActionDropdown
                    title={t('pages.exercises.buttons.database.advanced')}
                    variant="secondary"
                    className="me-1 mb-1"
                    disabled={isExecuting}
                    buttons={[
                        {
                            label: t('pages.exercises.buttons.database.list_constraints'),
                            onClick: handleListConstraints,
                            disabled: isExecuting,
                        },
                        {
                            label: t('pages.exercises.buttons.database.list_users'),
                            onClick: handleListUsers,
                            disabled: isExecuting,
                        }
                    ]}
                />

            </div>
        </>
    );
}

export default ButtonsDatabase;
