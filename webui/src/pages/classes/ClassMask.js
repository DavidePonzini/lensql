// Data placeholder for class data
function ClassMask({ title, setTitle, dataset, setDataset }) {
    return (
        <>
            <div className="mb-3">
                <label className="form-label">Title</label>
                <input type="text" className="form-control" defaultValue={title} onInput={(e) => setTitle(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Dataset</label>
                <textarea className="form-control" rows="3" defaultValue={dataset} onInput={(e) => setDataset(e.target.value)}></textarea>
            </div>
        </>
    );
}

export default ClassMask;