function AssignmentCard({ children, assignmentId, isGenerated = false, deadlineDate, submissionDate }) {
    function handleOpenAssignment() {
        // TODO: replace this elem with Query assignment=this.assignment
    }

    return (
        <div className="assignment">
            <p>{children}</p>
            <a
                href={`/assignments/${assignmentId}`}
                className="btn btn-primary"
                onClick={handleOpenAssignment()}
            >
                View Assignment
            </a>
        </div>
    );
}

export default AssignmentCard;