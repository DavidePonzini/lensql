import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

function ItemAssignmentList({
    fetchItems,
    assignAction,
    title = null,
    disabledItems = [],
}) {
    const { t } = useTranslation();
    const [items, setItems] = useState([]);
    const [selectAll, setSelectAll] = useState(false);

    async function handleAssign(id, value) {
        await assignAction(id, value);
        setItems((prev) =>
            prev.map((item) => (item.id === id ? { ...item, isAssigned: value } : item))
        );
    }

    async function handleSelectAll(value) {
        setSelectAll(value);
        setItems((prev) =>
            prev.map((item) => (disabledItems.includes(item.id) ? item : { ...item, isAssigned: value }))
        );
        await Promise.all(
            items
                .filter((item) => !disabledItems.includes(item.id))
                .map((item) => assignAction(item.id, value))
        );
    }

    useEffect(() => {
        async function fetchData() {
            const data = await fetchItems();
            setItems(data);
        }
        fetchData();
    }, [fetchItems]);

    useEffect(() => {
        const allAssigned = items.length > 0 && items.every((i) => i.isAssigned);
        setSelectAll(allAssigned);
    }, [items]);

    return (
        <div className="mb-3">
            <label className="form-label">
                {title || t('components.assignmentList.title')}
            </label>

            {items.length > 0 && (
                <div className="form-check mb-2">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        id="select-all"
                        checked={selectAll}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="select-all">
                        {t('components.assignmentList.select_all')}
                    </label>
                </div>
            )}

            {items.map((item) => (
                <div key={item.id} className="form-check">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        checked={item.isAssigned}
                        id={`item-${item.id}`}
                        disabled={disabledItems.includes(item.id)}
                        onChange={(e) => handleAssign(item.id, e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor={`item-${item.id}`}>
                        {item.label}
                    </label>
                </div>
            ))}
        </div>
    );
}

export default ItemAssignmentList;
