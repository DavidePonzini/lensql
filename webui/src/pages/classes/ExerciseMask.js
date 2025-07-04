// Data placeholder for exercise data
function ExerciseMask({ title, setTitle, request, setRequest, answer, setAnswer }) {
    return (
        <>
            <div className="mb-3">
                <label className="form-label">Title</label>
                <input type="text" className="form-control" defaultValue={title} onInput={(e) => setTitle(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Request</label>
                <textarea className="form-control" rows="3" defaultValue={request} onInput={(e) => setRequest(e.target.value)}></textarea>
            </div>
            <div className="mb-3">
                <label className="form-label">Answer</label>
                <textarea className="form-control" rows="3" defaultValue={answer} onInput={(e) => setAnswer(e.target.value)}></textarea>
            </div>
        </>
    );
}

export default ExerciseMask;