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

                <ButtonActionDropdown
                    title={t('pages.exercises.buttons.database.list_tables')}
                    disabled={isExecuting}
                    variant="secondary"
                    className="me-1 mb-1"
                    buttons={[
                        {
                            label: t('pages.exercises.buttons.database.list_tables_current'),
                            onClick: handleListTables,
                            disabled: isExecuting,
                        },
                        {
                            label: t('pages.exercises.buttons.database.list_tables_all'),
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
                    {t('pages.exercises.buttons.database.list_schemas')}
                </ButtonAction>

                <ButtonAction
                    variant="secondary"
                    className="me-1 mb-1"
                    onClick={handleListConstraints}
                    disabled={isExecuting}
                >
                    {t('pages.exercises.buttons.database.list_constraints')}
                </ButtonAction>
            </div>
        </>
    );
}

export default ButtonsDatabase;
