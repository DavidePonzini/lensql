function Message({ children, feedback = false }) {
    return (
        <div className="message">
            <div dangerouslySetInnerHTML={{ __html: children }} />

            {feedback && (
                <div class="message-feedback">
                    <span class="feedback feedback-up" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Helpful">
                        <i class="far fa-thumbs-up" />
                    </span>
                    <span class="feedback feedback-down" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Not helpful">
                        <i class="far fa-thumbs-down" />
                    </span>
                </div>
            )}
        </div>
    );
}

export default Message;