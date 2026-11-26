import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
    PieChart, Pie, Cell,
    BarChart, Bar, XAxis, YAxis,
    ResponsiveContainer, Tooltip, LabelList, Text,
    LineChart, Line, CartesianGrid, Legend
} from 'recharts';

import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import ErrorDetailsDialog from "../ErrorDetailsDialog";
import CATEGORY_COLOR from '../../errorCategoryColors';

function LearningStatsErrors({ data: statsData, isTeacher = false, sampleData = null }) {
    const { t, i18n } = useTranslation();
    const locale = i18n.resolvedLanguage || 'en';

    const data = sampleData ?? statsData;
    const [selectedQueryGoal, setSelectedQueryGoal] = useState('all');
    const [selectedErrorId, setSelectedErrorId] = useState(null);
    const [barChartWidth, setBarChartWidth] = useState(0);

    const role = isTeacher ? 'teacher' : 'student';

    // ----------------------------------------------------------------------
    // REAL DATA
    // ----------------------------------------------------------------------
    const allErrors = data?.errors || [];
    const selectedGoalValue = selectedQueryGoal === 'submitted' ? 'CHECK_SOLUTION' : 'FOCUSED';
    const dataErrors = selectedQueryGoal === 'all'
        ? Object.values(allErrors.reduce((acc, row) => {
            const existing = acc[row.error_id];

            if (existing) {
                existing.count += row.count;
                return acc;
            }

            acc[row.error_id] = { ...row };
            return acc;
        }, {}))
        : allErrors.filter(({ query_goal }) => query_goal === selectedGoalValue);
    const dataTimeline = (data?.timeline || []).filter(
        ({ query_goal }) => selectedQueryGoal === 'all' || query_goal === selectedGoalValue
    );

    const CATEGORY_DESC = {
        SYN: t('errors.categories.syn.description'),
        SEM: t('errors.categories.sem.description'),
        LOG: t('errors.categories.log.description'),
        COM: t('errors.categories.com.description'),
    };

    // ----------------------------------------------------------------------
    // PIE DATA
    // ----------------------------------------------------------------------
    const categoryCounts = { SYN: 0, SEM: 0, LOG: 0, COM: 0 };
    for (const { count, category } of dataErrors) {
        categoryCounts[category] += count;
    }

    const categoryData = [
        { cat: 'SYN', name: t('errors.categories.syn.name'), value: categoryCounts.SYN },
        { cat: 'SEM', name: t('errors.categories.sem.name'), value: categoryCounts.SEM },
        { cat: 'LOG', name: t('errors.categories.log.name'), value: categoryCounts.LOG },
        { cat: 'COM', name: t('errors.categories.com.name'), value: categoryCounts.COM },
    ];

    // Remove categories with zero count
    for (let i = categoryData.length - 1; i >= 0; i--) {
        if (categoryData[i].value === 0) {
            categoryData.splice(i, 1);
        }
    }

    // ----------------------------------------------------------------------
    // PER-ERROR BAR DATA
    // ----------------------------------------------------------------------
    const perErrorData = [...dataErrors]
        .sort((a, b) => b.count - a.count)
        .map(({ error_id, count, category }) => ({
            id: error_id,
            count,
            name: t(`errors.errors.${error_id}.name`),
            cat: category,
        }));

    const hasAnyStats = allErrors.length > 0 || (data?.timeline?.length ?? 0) > 0;
    const hasErrors = dataErrors.length > 0;
    const selectedError = perErrorData.find(error => error.id === selectedErrorId);
    const axisWidth = Math.min(200, Math.round(barChartWidth * 0.48));
    const toggleErrorDetails = id => setSelectedErrorId(current => current === id ? null : id);

    // ----------------------------------------------------------------------
    // TIMELINE: ERRORS PER QUERY BY DAY
    // ----------------------------------------------------------------------
    const timelineMap = new Map();
    const categories = Object.keys(CATEGORY_COLOR);

    for (const { date, query_count, errors } of dataTimeline) {
        if (!timelineMap.has(date)) {
            timelineMap.set(date, { date, queryCount: 0, SYN: 0, SEM: 0, LOG: 0, COM: 0 });
        }
        const day = timelineMap.get(date);
        day.queryCount += query_count;
        for (const category of categories) {
            day[category] += errors[category] ?? 0;
        }
    }

    const timelineData = Array.from(timelineMap.values())
        .sort((a, b) => a.date.localeCompare(b.date))
        .map(({ date, queryCount, ...errors }) => ({
            dateFormatted: new Date(date).toLocaleDateString(locale, {
                month: 'short',
                day: 'numeric',
                timeZone: 'UTC',
            }),
            ...Object.fromEntries(categories.map(category => [category, errors[category] / queryCount])),
        }));

    // ----------------------------------------------------------------------
    // TOOLTIP FUNCTIONS
    // ----------------------------------------------------------------------
    const pieTooltip = ({ payload }) => {
        if (!payload || !payload.length)
            return null;

        const { name, value, payload: p } = payload[0];
        const color = CATEGORY_COLOR[p.cat];

        return (
            <div style={{ background: '#fff', border: '1px solid #ccc', padding: '5px 10px' }}>
                <strong style={{ borderInlineStart: `4px solid ${color}`, paddingInlineStart: '0.5rem' }}>{name}</strong><br />
                {CATEGORY_DESC[p.cat]}<br />
                {t('components.learningStats.errors.count_label', { count: value })}
            </div>
        );
    };

    return (
        <>
            {!hasAnyStats ? (
                <p className="text-muted learning-stats-empty" style={{ fontSize: '1.1rem' }}>
                    {t(`components.learningStats.errors.empty.${role}`)}
                </p>
            ) : (
                <>
                    {!sampleData && <div className="learning-stats-filter mb-3">
                        <label className="text-muted" htmlFor="error-query-goal-filter">
                            {t('components.learningStats.errors.query_goal.label')}
                        </label>
                        <select
                            id="error-query-goal-filter"
                            className="form-select w-auto"
                            value={selectedQueryGoal}
                            onChange={(event) => setSelectedQueryGoal(event.target.value)}
                        >
                            <option value="all">{t('components.learningStats.errors.query_goal.options.all')}</option>
                            <option value="focused">{t('components.learningStats.errors.query_goal.options.focused')}</option>
                            <option value="submitted">{t('components.learningStats.errors.query_goal.options.submitted')}</option>
                        </select>
                    </div>}
                    {!hasErrors && (
                        <p className="text-muted learning-stats-empty" style={{ fontSize: '1.1rem' }}>
                            {t(`components.learningStats.errors.empty.${role}`)}
                        </p>
                    )}
                    {(hasErrors || timelineData.length > 0) && (
                        <>
                            <Row className="g-4 mb-4">
                                {/* PIE */}
                                {hasErrors && <Col xs={12} lg={timelineData.length > 0 ? 6 : 12}>
                                    <Card className="learning-stats-panel">
                                        <Card.Header>
                                            <Card.Title>{t('components.learningStats.errors.kind_title')}</Card.Title>
                                            <Card.Subtitle className="text-muted">
                                                {t(`components.learningStats.errors.kind_subtitle.${role}`)}
                                            </Card.Subtitle>
                                        </Card.Header>
                                        <Card.Body>
                                            <ResponsiveContainer width="100%" height={250}>
                                                <PieChart>
                                                    <Tooltip content={pieTooltip} wrapperStyle={{ zIndex: 1000 }}/>
                                                    <Pie
                                                        data={categoryData}
                                                        dataKey="value"
                                                        nameKey="name"
                                                        outerRadius={80}
                                                        label={({ name }) => name}
                                                    >
                                                        {categoryData.map(entry => (
                                                            <Cell key={entry.cat} fill={CATEGORY_COLOR[entry.cat]} />
                                                        ))}
                                                    </Pie>
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </Card.Body>
                                    </Card>
                                </Col>}

                                {/* TIMELINE */}
                                {timelineData.length > 0 && <Col xs={12} lg={hasErrors ? 6 : 12}>
                                    <Card className="learning-stats-panel">
                                        <Card.Header>
                                            <Card.Title>{t(`components.learningStats.errors.timeline_title.${role}`)}</Card.Title>
                                            <Card.Subtitle className="text-muted">
                                                {t(`components.learningStats.errors.timeline_subtitle.${role}`)}
                                            </Card.Subtitle>
                                        </Card.Header>
                                        <Card.Body>
                                            <ResponsiveContainer width="100%" height={300}>
                                                <LineChart data={timelineData} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                                                    <CartesianGrid strokeDasharray="3 3" />

                                                    <XAxis dataKey="dateFormatted" />
                                                    <YAxis domain={[0, dataMax => dataMax || 1]} tickFormatter={v => v.toLocaleString(locale)} />

                                                    <Tooltip
                                                        itemStyle={{ color: 'var(--bs-body-color)' }}
                                                        formatter={(value, name) => {
                                                            const label = t(`errors.categories.${name.toLowerCase()}.name`);
                                                            return [value.toLocaleString(locale, { maximumFractionDigits: 3 }), label];
                                                        }}
                                                        itemSorter={(entry) => {
                                                            const ORDER = { COM: 1, LOG: 2, SEM: 3, SYN: 4 };
                                                            return ORDER[entry.dataKey];
                                                        }}
                                                        wrapperStyle={{ zIndex: 1000 }}
                                                    />

                                                    <Legend formatter={(v) => (
                                                        <span className="text-body">{t(`errors.categories.${v.toLowerCase()}.name`)}</span>
                                                    )} />

                                                    <Line
                                                        type="linear"
                                                        dataKey="SYN"
                                                        dot={{ r: 2 }}
                                                        stroke={CATEGORY_COLOR.SYN}
                                                        strokeWidth={2}
                                                    />
                                                    <Line
                                                        type="linear"
                                                        dataKey="SEM"
                                                        dot={{ r: 2 }}
                                                        stroke={CATEGORY_COLOR.SEM}
                                                        strokeWidth={2}
                                                    />
                                                    <Line
                                                        type="linear"
                                                        dataKey="LOG"
                                                        dot={{ r: 2 }}
                                                        stroke={CATEGORY_COLOR.LOG}
                                                        strokeWidth={2}
                                                    />
                                                    <Line
                                                        type="linear"
                                                        dataKey="COM"
                                                        dot={{ r: 2 }}
                                                        stroke={CATEGORY_COLOR.COM}
                                                        strokeWidth={2}
                                                    />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        </Card.Body>
                                    </Card>
                                </Col>}
                            </Row>

                            {hasErrors && <Row className="mb-4">
                                {/* BAR */}
                                <Col>
                                    <Card className="learning-stats-panel">
                                        <Card.Header>
                                            <Card.Title>{t('components.learningStats.errors.common_title')}</Card.Title>
                                            <Card.Subtitle className="text-muted">
                                                {t(`components.learningStats.errors.common_subtitle.${role}`)}
                                            </Card.Subtitle>
                                        </Card.Header>
                                        <Card.Body>
                                            <p className="bg-body-tertiary border rounded px-3 py-2 mb-4">
                                                {t('components.learningStats.errors.details_hint')}
                                            </p>
                                            <ResponsiveContainer width="100%" height={40 * perErrorData.length} onResize={setBarChartWidth}>
                                                <BarChart layout="vertical" data={perErrorData} margin={{ left: 0, right: 32 }}>
                                                    <XAxis type="number" hide />
                                                    <YAxis
                                                        type="category"
                                                        dataKey="id"
                                                        width={axisWidth}
                                                        tick={({ payload, x, y, textAnchor, verticalAnchor, fill }) => (
                                                            <g
                                                                role="button"
                                                                tabIndex={0}
                                                                aria-haspopup="dialog"
                                                                aria-label={perErrorData.find(error => error.id === payload.value)?.name}
                                                                onClick={() => toggleErrorDetails(payload.value)}
                                                                onKeyDown={event => {
                                                                    if (event.key === 'Enter' || event.key === ' ') {
                                                                        event.preventDefault();
                                                                        toggleErrorDetails(payload.value);
                                                                    }
                                                                }}
                                                                style={{ cursor: 'help' }}
                                                            >
                                                                <Text
                                                                    x={x}
                                                                    y={y}
                                                                    textAnchor={textAnchor}
                                                                    verticalAnchor={verticalAnchor}
                                                                    fill={fill}
                                                                    width={Math.max(0, axisWidth - 8)}
                                                                    maxLines={2}
                                                                    style={{ fontWeight: payload.value === selectedError?.id ? 700 : 400 }}
                                                                >
                                                                    {perErrorData.find(error => error.id === payload.value)?.name}
                                                                </Text>
                                                            </g>
                                                        )}
                                                    />
                                                    <Bar
                                                        dataKey="count"
                                                        onClick={({ payload }) => toggleErrorDetails(payload.id)}
                                                        isAnimationActive={false}
                                                        shape={(props) => {
                                                            const barColor = CATEGORY_COLOR[props.payload.cat];
                                                            return (
                                                                <rect
                                                                    x={props.x}
                                                                    y={props.y}
                                                                    width={props.width}
                                                                    height={props.height}
                                                                    cursor="help"
                                                                    fill={barColor}
                                                                    fillOpacity={selectedError && props.payload.id !== selectedError.id ? 0.3 : 1}
                                                                />
                                                            );
                                                        }}
                                                    >
                                                        <LabelList dataKey="count" position="right" fill="#000" />
                                                    </Bar>
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </Card.Body>
                                    </Card>
                                </Col>
                            </Row>}
                        </>
                    )}
                </>
            )}
            <ErrorDetailsDialog
                id={selectedError?.id}
                title={selectedError?.name}
                onHide={() => setSelectedErrorId(null)}
            >
                {selectedError && (
                    <span>{t('components.learningStats.errors.count_label', { count: selectedError.count })}</span>
                )}
            </ErrorDetailsDialog>
        </>
    );
}

export default LearningStatsErrors;
