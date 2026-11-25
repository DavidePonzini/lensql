import { useTranslation } from 'react-i18next';

import './ErrorDetails.css';

function ErrorDetails({ id, title, heading: Heading = 'h2', children }) {
    const { t } = useTranslation();
    const errorKey = `errors.errors.${id}`;
    const labelKey = 'components.learningStats.errors';

    return (
        <div className="error-details">
            <Heading className="h4 fw-semibold">{title}</Heading>
            <p className="mb-0">{t(`${errorKey}.description`)}</p>
            {children}
            <hr />
            <p className="h5 text-danger">{t(`${labelKey}.example_label`)}</p>
            <pre className="error-details__sql error-details__sql--example"><code>{t(`${errorKey}.example`)}</code></pre>
            <p className="h5 text-info mt-3">{t(`${labelKey}.explanation_label`)}</p>
            <p className="fst-italic mb-0">{t(`${errorKey}.explanation`)}</p>
            <p className="h5 text-success mt-3">{t(`${labelKey}.correction_label`)}</p>
            <pre className="error-details__sql error-details__sql--correction mb-0"><code>{t(`${errorKey}.correction`)}</code></pre>
        </div>
    );
}

export default ErrorDetails;
