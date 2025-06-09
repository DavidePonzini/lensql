import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";

function ButtonActionDropdown({ title, disabled = false, locked = false, variant, className = "", buttons }) {
    return (
        <DropdownButton
            className={`btn-group ${className}`}
            title={locked ?
                <>
                    <i className="fa-solid fa-lock me-1" />
                    {title}
                </>
                : title
            }
            disabled={disabled || locked}
            variant={variant}
        >
            {buttons.map(({ label, onClick, disabled = false, locked = false, cost = null }, key) => (
                <Dropdown.Item
                    key={key}
                    onClick={onClick}
                    disabled={disabled || locked}
                    className={locked ? 'text-muted' : ''}
                    title={label}
                >
                    {locked && <i className="fa-solid fa-lock me-1" />}
                    {label}
                    {cost && cost > 0 && (
                        <span className="ms-2">
                            <i className="fa-solid fa-coins" /> {cost}
                        </span>
                    )}
                </Dropdown.Item>
            ))}
        </DropdownButton>
    );
}

export default ButtonActionDropdown;