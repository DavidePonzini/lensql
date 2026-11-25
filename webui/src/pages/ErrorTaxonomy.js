import { useEffect, useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import ErrorDetailsDialog from '../components/ErrorDetailsDialog';
import useAuth from '../hooks/useAuth';
import './ErrorTaxonomy.css';

const pageKey = 'pages.errorTaxonomy';

function ErrorTaxonomy() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { errorId: requestedId = '' } = useParams();
    const { state } = useLocation();
    const navigate = useNavigate();
    const [taxonomy, setTaxonomy] = useState(null);
    const [failed, setFailed] = useState(false);
    const [search, setSearch] = useState('');
    const [expanded, setExpanded] = useState(undefined);
    const [includeDeprecated, setIncludeDeprecated] = useState(false);
    const query = search.trim().toLowerCase();
    const requestedError = taxonomy?.errors.find(error => String(error.id) === requestedId);
    const showDeprecated = includeDeprecated || requestedError?.deprecated === true;

    function closeDetails() {
        setExpanded({ requestedId: '', category: requestedError.category });
        if (state?.fromTaxonomyList) navigate(-1);
        else navigate('/error-taxonomy', { replace: true });
    }

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
            description: t(`errors.errors.${error.id}.description`),
        }))
        .filter(error => /^\d+$/.test(query)
            ? String(error.id) === query
            : `${error.name} ${error.description}`.toLowerCase().includes(query));
    const categories = (taxonomy?.categories ?? []).map(id => ({
        id,
        errors: visibleErrors.filter(error => error.category === id),
    })).filter(category => category.errors.length > 0);
    const defaultCategory = categories.find(category => category.id === requestedError?.category)?.id ?? categories[0]?.id;
    const expandedCategory = expanded?.requestedId === requestedId ? expanded.category : defaultCategory;
    const openCategory = expandedCategory === null || categories.some(category => category.id === expandedCategory)
        ? expandedCategory
        : defaultCategory ?? null;

    return (
        <div className="container-md py-4">
            <h1 className="text-primary">{t(`${pageKey}.title`)}</h1>
            <p className="lead">{t(`${pageKey}.intro`)}</p>

            {failed && <p role="alert">{t(`${pageKey}.loadError`)}</p>}
            {!taxonomy && !failed && <p role="status">{t(`${pageKey}.loading`)}</p>}
            {taxonomy && (
                <>
                    <label htmlFor="taxonomy-search" className="form-label">{t(`${pageKey}.search`)}</label>
                    <input
                        id="taxonomy-search"
                        type="search"
                        className="form-control mb-2"
                        value={search}
                        onChange={event => {
                            setSearch(event.target.value);
                            setExpanded(undefined);
                        }}
                    />
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
                    <Accordion
                        activeKey={openCategory}
                        onSelect={category => setExpanded({ requestedId, category })}
                    >
                        {categories.map(({ id, errors }) => {
                            const key = `errors.categories.${id.toLowerCase()}`;
                            return (
                                <Accordion.Item eventKey={id} key={id}>
                                    <Accordion.Header as="h2">{t(`${key}.name`)}</Accordion.Header>
                                    <Accordion.Body className="p-2">
                                        <p className="small text-body-secondary px-2 mb-2">{t(`${key}.description`)}</p>
                                        <ul className="list-group list-group-flush error-taxonomy-entries">
                                            {errors.map(error => (
                                                <li
                                                    key={error.id}
                                                    className={`list-group-item p-0${requestedError?.id === error.id ? ' active' : ''}`}
                                                >
                                                    <Link
                                                        className="list-group-item-action d-flex gap-2 px-3 py-2 text-decoration-none"
                                                        aria-haspopup="dialog"
                                                        to={`/error-taxonomy/${error.id}`}
                                                        state={{ fromTaxonomyList: true }}
                                                    >
                                                        <span className="error-taxonomy-id text-end flex-shrink-0">{error.id}</span>
                                                        <span>
                                                            {error.name}
                                                            {error.deprecated && <small className="d-block">{t(`${pageKey}.deprecated`)}</small>}
                                                        </span>
                                                    </Link>
                                                </li>
                                            ))}
                                        </ul>
                                    </Accordion.Body>
                                </Accordion.Item>
                            );
                        })}
                    </Accordion>
                </>
            )}
            <ErrorDetailsDialog
                id={requestedError?.id}
                title={requestedError && `${requestedError.id}. ${t(`errors.errors.${requestedError.id}.name`)}`}
                onHide={closeDetails}
            >
                {requestedError?.deprecated && (
                    <p className="small text-body-secondary mt-2 mb-0">{t(`${pageKey}.deprecated`)}</p>
                )}
            </ErrorDetailsDialog>
        </div>
    );
}

export default ErrorTaxonomy;
