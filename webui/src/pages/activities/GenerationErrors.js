import { useState } from 'react';
import { Accordion } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

export default function GenerationErrors({ options, counts, setCounts, busy }) {
    const { t } = useTranslation();
    const key = 'pages.activities.generate';
    const [search, setSearch] = useState('');
    const [selectedOnly, setSelectedOnly] = useState(false);
    const [topOnly, setTopOnly] = useState(false);
    const [hideUnsupported, setHideUnsupported] = useState(true);
    const [expanded, setExpanded] = useState(['SYN']);
    const difficulties = [1, 2, 3];
    const selectedCount = error => difficulties.reduce((sum, difficulty) => sum + Number(counts[`${error.id}:${difficulty}`] || 0), 0);
    const query = search.trim().toLowerCase();
    const localizedErrors = options.errors.map(error => ({
        ...error,
        name: t(`errors.errors.${error.id}.name`),
        description: t(`errors.errors.${error.id}.description`),
    }));
    const categories = options.categories.map(category => ({
        ...category,
        name: t(`errors.categories.${category.id.toLowerCase()}.name`),
        description: t(`errors.categories.${category.id.toLowerCase()}.description`),
        errors: localizedErrors.filter(error => error.category === category.id
            && (!topOnly || error.common_rank)
            && (!hideUnsupported || error.supported)
            && (!selectedOnly || selectedCount(error) > 0)
            && (!query || `${error.id} ${error.name} ${error.description}`.toLowerCase().includes(query))),
    })).filter(category => category.errors.length);

    return <section aria-label={t(`${key}.errors`)}>
        <h5>{t(`${key}.targets_heading`)}</h5>
        <p className="text-body-secondary">{t(`${key}.difficulty_help`)}</p>
        <div className="row g-2 align-items-center mb-3">
            <div className="col-sm">
                <label htmlFor="generation-search" className="visually-hidden">{t(`${key}.search`)}</label>
                <input id="generation-search" type="search" className="form-control" placeholder={t(`${key}.search`)}
                    value={search} onChange={event => setSearch(event.target.value)} />
            </div>
            <div className="col-sm-auto form-check ms-3 me-2">
                <input id="generation-top-only" type="checkbox" className="form-check-input" checked={topOnly}
                    onChange={event => setTopOnly(event.target.checked)} />
                <label className="form-check-label" htmlFor="generation-top-only">{t(`${key}.top_only`)}</label>
            </div>
            <div className="col-sm-auto form-check ms-3 me-2">
                <input id="generation-hide-unsupported" type="checkbox" className="form-check-input" checked={hideUnsupported}
                    onChange={event => setHideUnsupported(event.target.checked)} />
                <label className="form-check-label" htmlFor="generation-hide-unsupported">{t(`${key}.hide_unsupported`)}</label>
            </div>
            <div className="col-sm-auto form-check ms-3 me-2">
                <input id="generation-selected-only" type="checkbox" className="form-check-input" checked={selectedOnly}
                    onChange={event => setSelectedOnly(event.target.checked)} />
                <label className="form-check-label" htmlFor="generation-selected-only">{t(`${key}.selected_only`)}</label>
            </div>
        </div>
        {!categories.length && <p>{t(`${key}.no_errors`)}</p>}
        <Accordion alwaysOpen activeKey={query || selectedOnly || topOnly ? categories.map(category => category.id) : expanded}
            onSelect={value => setExpanded(value || [])}>
            {categories.map(category => <Accordion.Item eventKey={category.id} key={category.id}>
                <Accordion.Header>
                    {category.name}
                    <span className="badge text-bg-secondary ms-2">{options.errors.filter(error => error.category === category.id).reduce((sum, error) => sum + selectedCount(error), 0)}</span>
                </Accordion.Header>
                <Accordion.Body>
                    <p className="text-body-secondary">{category.description}</p>
                    <div className="table-responsive">
                        <table className="table align-middle mb-0">
                            <thead><tr><th scope="col">{t(`${key}.error_label`)}</th>
                                {difficulties.map(difficulty => <th scope="col" className="text-center" key={difficulty}>{t(`${key}.difficulty_${difficulty}`)}</th>)}
                            </tr></thead>
                            <tbody>{category.errors.map(error => <tr key={error.id} className={error.supported ? undefined : 'text-body-secondary'}>
                                <th scope="row" className="fw-normal" style={{ minWidth: '15rem' }}>
                                    <strong>{error.id}. {error.name}</strong>
                                    {error.common_rank && <span className="badge text-bg-primary ms-2" title={t(`${key}.common_error_help`)}>{t(`${key}.common_error`, { rank: error.common_rank })}</span>}
                                    {!error.supported && <span className="badge text-bg-secondary ms-2">{t(`${key}.unsupported`)}</span>}
                                    <p className="small text-body-secondary mb-0">{error.description}</p>
                                </th>
                                {difficulties.map(difficulty => {
                                    const countKey = `${error.id}:${difficulty}`;
                                    return <td key={difficulty}><input className="form-control text-center mx-auto" style={{ width: '5rem' }}
                                        aria-label={`${error.name} — ${t(`${key}.difficulty_${difficulty}`)}`}
                                        type="number" min="0" max="100" step="1" value={counts[countKey] ?? 0} disabled={busy || !error.supported}
                                        onChange={event => setCounts(previous => ({ ...previous, [countKey]: event.target.value }))} /></td>;
                                })}
                            </tr>)}</tbody>
                        </table>
                    </div>
                </Accordion.Body>
            </Accordion.Item>)}
        </Accordion>
    </section>;
}
