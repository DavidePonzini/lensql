import { useId } from 'react';
import { useTranslation } from 'react-i18next';
import Modal from 'react-bootstrap/Modal';

import ErrorDetails from './ErrorDetails';

function ErrorDetailsDialog({ id, title, onHide, children }) {
    const { t } = useTranslation();
    const titleId = useId();

    return (
        <Modal
            show={id != null}
            onHide={onHide}
            aria-labelledby={titleId}
            className="error-details-dialog"
            backdropClassName="error-details-backdrop"
            centered
            scrollable
            size="lg"
            animation={false}
        >
            <Modal.Header closeButton closeLabel={t('components.buttons.modal.close')}>
                <Modal.Title as="h2" id={titleId}>
                    {t('components.learningStats.errors.details_label')}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {id != null && (
                    <ErrorDetails id={id} title={title} heading="h3">{children}</ErrorDetails>
                )}
            </Modal.Body>
        </Modal>
    );
}

export default ErrorDetailsDialog;
