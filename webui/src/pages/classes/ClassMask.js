// Data placeholder for class data
function ClassMask({ title, setTitle, dataset, setDataset }) {
    return (
        <>
            <div className="mb-3">
                <label className="form-label">Title</label>
                <input type="text" className="form-control" defaultValue={title} onInput={(e) => setTitle(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Dataset (Optional)</label>
                <textarea className="form-control monospace" rows="10" defaultValue={dataset} onInput={(e) => setDataset(e.target.value)}></textarea>
                <div>
                    <b>Tips</b>
                    <ul>
                        <li>Include the whole script into a <code>BEGIN; ... COMMIT;</code> block</li>
                        <li>Begin the script with <code>DROP SCHEMA IF EXISTS schema_name CASCADE;</code></li>
                        <li>Use a unique <code>search_path</code> for each dataset</li>
                        <li>Group insertions into a single <code>INSERT INTO</code> statement for each table to greatly improve performance</li>
                    </ul>
                </div>
            </div>
        </>
    );
}

export default ClassMask;