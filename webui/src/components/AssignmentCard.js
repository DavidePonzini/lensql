function AssignmentCard({ children, href, isGenerated = false }) {
    return (
        <div className="assignment">
            <div className="assignment-header">
                <h2>{children}</h2>
                {isGenerated && <span className="badge bg-secondary">Generated</span>}
            </div>
            <div className="assignment-body">
                <p>{children}</p>
                <a href={href} className="btn btn-primary">View Assignment</a>
            </div>
        </div>
    );
}

export default AssignmentCard;