function AssignmentCard({ children, assignmentId, isGenerated = false }) {
    function handleOpenAssignment() {
        // TODO: replace this elem with Query assignment=this.assignment
    }

    return (
        <div className="assignment">
            <div className="assignment-header">
                <h2>{children}</h2>
                {isGenerated && <span className="badge bg-secondary">Generated</span>}
            </div>
            <div className="assignment-body">
                <p>{children}</p>
                <button className="btn btn-primary" onClick={handleOpenAssignment()}>View Assignment</button>
            </div>
        </div>
    );
}

export default AssignmentCard;