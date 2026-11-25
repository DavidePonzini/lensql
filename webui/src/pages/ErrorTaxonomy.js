import { useEffect, useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

import ErrorDetails from '../components/ErrorDetails';
import useAuth from '../hooks/useAuth';

const pageKey = 'pages.errorTaxonomy';

function ErrorTaxonomy() {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { errorId: requestedId = '' } = useParams();
    const navigate = useNavigate();
    const [taxonomy, setTaxonomy] = useState(null);
    const [failed, setFailed] = useState(false);
    const [search, setSearch] = useState('');
    const [expanded, setExpanded] = useState(undefined);
    const [includeDeprecated, setIncludeDeprecated] = useState(false);
    const query = search.trim().toLowerCase();
    const requestedError = taxonomy?.errors.find(error => String(error.id) === requestedId);
    const showDeprecated = includeDeprecated || requestedError?.deprecated === true;

    function selectError(id) {
        const nextId = id === null ? '' : String(id);
        if (nextId !== requestedId) navigate(nextId ? `/error-taxonomy/${nextId}` : '/error-taxonomy');
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
    const selected = visibleErrors.find(error => error.id === requestedError?.id) ?? categories[0]?.errors[0];
    const expandedCategory = expanded?.requestedId === requestedId ? expanded.category : selected?.category;
    const openCategory = expandedCategory === null || categories.some(category => category.id === expandedCategory)
        ? expandedCategory
        : selected?.category ?? null;

    return (
        <div className="container-md py-4">
            <h1 className="text-primary">{t(`${pageKey}.title`)}</h1>
            <p className="lead">{t(`${pageKey}.intro`)}</p>

            {failed && <p role="alert">{t(`${pageKey}.loadError`)}</p>}
            {!taxonomy && !failed && <p role="status">{t(`${pageKey}.loading`)}</p>}
            {taxonomy && (
                <div className="row g-4">
                    <div className="col-md-5 col-lg-4">
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
                                onChange={event => {
                                    setIncludeDeprecated(event.target.checked);
                                    if (!event.target.checked && requestedError?.deprecated) selectError(null);
                                }}
                            />
                            <label htmlFor="taxonomy-show-deprecated" className="form-check-label">
                                {t(`${pageKey}.showDeprecated`)}
                            </label>
                        </div>

                        {!categories.length && <p role="status">{t(`${pageKey}.empty`)}</p>}
                        <div className="error-taxonomy-list">
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
                                                <div className="list-group list-group-flush">
                                                    {errors.map(error => (
                                                        <button
                                                            type="button"
                                                            key={error.id}
                                                            className={`list-group-item list-group-item-action${selected?.id === error.id ? ' active' : ''}`}
                                                            aria-pressed={selected?.id === error.id}
                                                            onClick={() => selectError(error.id)}
                                                        >
                                                            {error.id}. {error.name}
                                                            {error.deprecated && <small className="d-block">{t(`${pageKey}.deprecated`)}</small>}
                                                        </button>
                                                    ))}
                                                </div>
                                            </Accordion.Body>
                                        </Accordion.Item>
                                    );
                                })}
                            </Accordion>
                        </div>
                    </div>

                    <div className="col-md-7 col-lg-8" aria-live="polite">
                        {selected && (
                            <ErrorDetails id={selected.id} title={`${selected.id}. ${selected.name}`}>
                                {selected.deprecated && (
                                    <p className="small text-body-secondary mt-2 mb-0">{t(`${pageKey}.deprecated`)}</p>
                                )}
                            </ErrorDetails>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ErrorTaxonomy;
