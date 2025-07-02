import { useEffect, useState } from 'react';

function ItemAssignmentList({
    fetchItems,             // async () => [{ id, label, isAssigned }]
    assignAction,           // async (id: string, value: boolean) => void
    title = 'Assign to',    // UI label above the list
}) {
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

        // Update UI optimistically
        setItems((prev) => prev.map((item) => ({ ...item, isAssigned: value })));
        
        // Send requests for all entities
        await Promise.all(
            items.map((item) => assignAction(item.id, value))
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
            <label className="form-label">{title}</label>

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
                        Select All
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
