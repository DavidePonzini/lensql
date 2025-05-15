import { useState } from "react";
import { Modal, Button } from "react-bootstrap";

function ButtonModal({
    className,
    title,
    buttonText,
    children,
    footerButtons, // Array of buttons to render in the footer
    size = "md",
}) {
    const [showModal, setShowModal] = useState(false);

    function handleClose() { setShowModal(false); }
    function handleShow() { setShowModal(true); }

    return (
        <>
            <button type="button" className={className} onClick={handleShow}>
                {buttonText}
            </button>

            <Modal show={showModal} onHide={(handleClose)} centered size={size}>
                <Modal.Header closeButton>
                    <Modal.Title>{title}</Modal.Title>
                </Modal.Header>
                <Modal.Body>{children}</Modal.Body>
                <Modal.Footer>
                    {footerButtons && (
                        footerButtons.map((btn, index) => (
                            <Button
                                key={index}
                                variant={btn.variant || "secondary"}
                                onClick={() => {
                                    btn.onClick?.();
                                    if (btn.autoClose !== false) handleClose();
                                }}
                            >
                                {btn.label}
                            </Button>
                        ))
                    )}

                    <Button variant="secondary" onClick={handleClose}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
}

export default ButtonModal;
