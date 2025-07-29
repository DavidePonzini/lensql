import { useTranslation } from 'react-i18next';
import Button from "react-bootstrap/Button";

function ButtonAction({ onClick, disabled = false, locked = false, variant, className = '', cost = null, children }) {
    const { t } = useTranslation();

    return (
        <Button
            variant={variant}
            className={className}
            onClick={onClick}
            disabled={disabled || locked}
            title={locked ? t('components.buttons.button.locked_tooltip') : ''}
        >
            {locked && <i className="fa-solid fa-lock me-1" />}
            {children}
            {cost !== null && (
                <span className="ms-2">
                    <i className="fa-solid fa-coins" /> {cost > 0 ? cost : t('components.buttons.button.free')}
                </span>
            )}
        </Button>
    );
}

export default ButtonAction;
