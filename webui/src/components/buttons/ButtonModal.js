import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Modal, Button } from "react-bootstrap";

function ButtonModal({
    variant = "primary",
    className,
    title,
    buttonText,
    children,
    footerButtons,
    size = "md",
    fullscreen = false,
    disabled = false,
}) {
    const { t } = useTranslation();
    const [showModal, setShowModal] = useState(false);

    function handleClose() { setShowModal(false); }
    function handleShow() { setShowModal(true); }

    return (
        <>
            <Button variant={variant} className={className} onClick={handleShow} disabled={disabled}>
                {buttonText}
            </Button>

            <Modal show={showModal} onHide={handleClose} centered size={size} fullscreen={fullscreen}>
                <Modal.Header closeButton>
                    <Modal.Title>{title}</Modal.Title>
                </Modal.Header>

                <Modal.Body>{children}</Modal.Body>

                <Modal.Footer>
                    {footerButtons?.map((btn, index) => (
                        <Button
                            key={index}
                            variant={btn.variant || "secondary"}
                            disabled={btn.disabled || false}
                            onClick={() => {
                                btn.onClick?.();
                                if (btn.autoClose !== false) handleClose();
                            }}
                        >
                            {btn.text}
                        </Button>
                    ))}

                    <Button variant="secondary" onClick={handleClose}>
                        {t('components.buttons.modal.close')}
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
}

export default ButtonModal;
