import { useEffect, useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';

import ErrorDetails from '../components/ErrorDetails';
import ERROR_CATEGORY_COLORS from '../errorCategoryColors';
import useAuth from '../hooks/useAuth';
import './ErrorTaxonomy.css';

const pageKey = 'pages.errorTaxonomy';
const defaultErrorId = '40';

function ErrorTaxonomy() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { errorId: requestedId = '' } = useParams();
    const navigate = useNavigate();
    const [taxonomy, setTaxonomy] = useState(null);
    const [failed, setFailed] = useState(false);
    const [collapsedErrorId, setCollapsedErrorId] = useState(null);
    const [includeDeprecated, setIncludeDeprecated] = useState(false);
    const requestedError = taxonomy?.errors.find(error => String(error.id) === requestedId);
    const showDeprecated = includeDeprecated || requestedError?.deprecated === true;

    useEffect(() => {
        let active = true;
        setFailed(false);

        apiRequest('/api/queries/error-taxonomy')
            .then(data => { if (active) setTaxonomy(data); })
            .catch(() => { if (active) setFailed(true); });

        return () => { active = false; };
    }, [apiRequest]);

    const visibleErrors = (taxonomy?.errors ?? [])
        .filter(error => showDeprecated || !error.deprecated)
        .map(error => ({
            ...error,
            name: t(`errors.errors.${error.id}.name`),
        }));
    const categories = (taxonomy?.categories ?? []).map(id => ({
        id,
        errors: visibleErrors.filter(error => error.category === id),
    })).filter(category => category.errors.length > 0);
    const defaultError = visibleErrors.find(error => String(error.id) === defaultErrorId);
    const selectedError = requestedError ?? defaultError ?? categories[0]?.errors[0];
    const openCategory = collapsedErrorId === requestedId ? null : selectedError?.category;

    function selectCategory(categoryId) {
        setCollapsedErrorId(categoryId == null ? requestedId : null);
        if (categoryId != null && categoryId !== selectedError?.category) {
            const firstError = categories.find(category => category.id === categoryId).errors[0];
            navigate(`/error-taxonomy/${firstError.id}`);
        }
    }

    return (
        <div className="container-md py-4">
            <h1 className="text-primary">{t(`${pageKey}.title`)}</h1>
            <p className="lead">{t(`${pageKey}.intro`)}</p>

            {failed && <p role="alert">{t(`${pageKey}.loadError`)}</p>}
            {!taxonomy && !failed && <p role="status">{t(`${pageKey}.loading`)}</p>}
            {taxonomy && (
                <>
                    {categories.length > 0 && (
                        <p className="small text-body-secondary mb-2">
                            {t('components.learningStats.errors.details_hint')}
                        </p>
                    )}
                    <div className="form-check mb-3">
                        <input
                            id="taxonomy-show-deprecated"
                            type="checkbox"
                            className="form-check-input"
                            checked={showDeprecated}
                            onChange={event => setIncludeDeprecated(event.target.checked)}
                        />
                        <label htmlFor="taxonomy-show-deprecated" className="form-check-label">
                            {t(`${pageKey}.showDeprecated`)}
                        </label>
                    </div>

                    {!categories.length && <p role="status">{t(`${pageKey}.empty`)}</p>}
                    <div className="error-taxonomy-layout">
                        <Accordion
                            activeKey={openCategory}
                            onSelect={selectCategory}
                        >
                            {categories.map(({ id, errors }) => {
                                const key = `errors.categories.${id.toLowerCase()}`;
                                return (
                                    <Accordion.Item
                                        eventKey={id}
                                        key={id}
                                        style={{ '--taxonomy-category-color': ERROR_CATEGORY_COLORS[id.toUpperCase()] }}
                                    >
                                        <Accordion.Header as="h2">{t(`${key}.name`)}</Accordion.Header>
                                        <Accordion.Body className="p-2">
                                            <p className="small text-body-secondary px-2 mb-2">{t(`${key}.description`)}</p>
                                            <ul className="list-group list-group-flush error-taxonomy-entries">
                                                {errors.map(error => (
                                                    <li
                                                        key={error.id}
                                                        className={`list-group-item p-0${selectedError?.id === error.id ? ' active' : ''}`}
                                                    >
                                                        <Link
                                                            className="error-taxonomy-link d-flex align-items-baseline gap-2 px-3 py-2 text-decoration-none"
                                                            aria-current={selectedError?.id === error.id ? 'true' : undefined}
                                                            to={`/error-taxonomy/${error.id}`}
                                                        >
                                                            <span className="error-taxonomy-id small text-end flex-shrink-0">{error.id}</span>
                                                            <span className="flex-grow-1">
                                                                <span className="fw-medium">{error.name}</span>
                                                                {error.deprecated && <small className="d-block">{t(`${pageKey}.deprecated`)}</small>}
                                                            </span>
                                                            <i className="bi bi-chevron-right error-taxonomy-chevron small" aria-hidden="true" />
                                                        </Link>
                                                    </li>
                                                ))}
                                            </ul>
                                        </Accordion.Body>
                                    </Accordion.Item>
                                );
                            })}
                        </Accordion>
                        {selectedError && (
                            <ErrorDetails
                                id={selectedError.id}
                                title={`${selectedError.id}. ${t(`errors.errors.${selectedError.id}.name`)}`}
                            >
                                {selectedError.deprecated && (
                                    <p className="small text-body-secondary mt-2 mb-0">{t(`${pageKey}.deprecated`)}</p>
                                )}
                            </ErrorDetails>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default ErrorTaxonomy;
