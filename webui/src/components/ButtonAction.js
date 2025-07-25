import Button from "react-bootstrap/Button";

function ButtonAction({ onClick, disabled = false, locked = false, variant, className = '', cost = null, children }) {
    return (
        <Button
            variant={variant}
            className={className}
            onClick={onClick}
            disabled={disabled || locked}
            title={locked ? "This action is locked" : ""}
        >
            {locked && <i className="fa-solid fa-lock me-1" />}
            {children}
            {cost !== null && (
                <span className="ms-2">
                    <i className="fa-solid fa-coins" /> {cost > 0 ? cost : 'Free'}
                </span>
            )}
        </Button>
    );
}

export default ButtonAction;