import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from "../../hooks/useAuth";

import {
    PieChart, Pie, Cell,
    BarChart, Bar, XAxis, YAxis,
    ResponsiveContainer, Tooltip, LabelList,
    AreaChart, Area, CartesianGrid, Legend
} from 'recharts';

import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import ObservedOnce from "../ObservedOnce";

function LearningStatsErrors({ datasetId = null, exerciseId = null, isTeacher = false }) {
    const { t, i18n } = useTranslation();
    const locale = i18n.resolvedLanguage || 'en';

    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/errors?dataset_id=${datasetId || ''}&exercise_id=${exerciseId || ''}&is_teacher=${isTeacher ? '1' : '0'}`,
            'GET'
        );
        setData(response.data);
    }

    const role = isTeacher ? 'teacher' : 'student';

    // ----------------------------------------------------------------------
    // REAL DATA
    // ----------------------------------------------------------------------
    const dataErrors = data?.errors || [];        // [{ error_id, count }]
    const dataTimeline = data?.timeline || [];    // [{ date, error_id, count }]

    // ----------------------------------------------------------------------
    // CATEGORY MAPPING
    // ----------------------------------------------------------------------
    function categoryOf(id) {
        if (id < 39) return 'syn';
        if (id < 52) return 'sem';
        if (id < 82) return 'log';
        return 'com';
    }

    const CATEGORY_COLOR = {
        syn: '#d9534f',
        sem: '#fd7e14',
        log: '#0d6efd',
        com: '#198754',
    };

    const CATEGORY_DESC = {
        syn: t('errors.categories.syn.description'),
        sem: t('errors.categories.sem.description'),
        log: t('errors.categories.log.description'),
        com: t('errors.categories.com.description'),
    };

    // ----------------------------------------------------------------------
    // PIE DATA
    // ----------------------------------------------------------------------
    const categoryCounts = { syn: 0, sem: 0, log: 0, com: 0 };
    for (const { error_id, count } of dataErrors) {
        categoryCounts[categoryOf(error_id)] += count;
    }

    const categoryData = [
        { cat: 'syn', name: t('errors.categories.syn.name'), value: categoryCounts.syn },
        { cat: 'sem', name: t('errors.categories.sem.name'), value: categoryCounts.sem },
        { cat: 'log', name: t('errors.categories.log.name'), value: categoryCounts.log },
        { cat: 'com', name: t('errors.categories.com.name'), value: categoryCounts.com },
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
        .map(({ error_id, count }) => ({
            id: error_id,
            count,
            name: t(`errors.errors.${error_id}.name`),
            cat: categoryOf(error_id),
        }));

    const hasErrors = dataErrors.length > 0;

    // ----------------------------------------------------------------------
    // TIMELINE: GROUP + NORMALIZE + FORMAT DATE
    // ----------------------------------------------------------------------
    const timelineMap = {};

    for (const row of dataTimeline) {
        const cat = categoryOf(row.error_id);
        const dateKey = new Date(row.date).toISOString().split('T')[0];

        if (!timelineMap[dateKey]) {
            timelineMap[dateKey] = { date: dateKey, syn: 0, sem: 0, log: 0, com: 0 };
        }
        timelineMap[dateKey][cat] += row.count;
    }

    // convert to array + percentages
    const timelineData = Object.values(timelineMap)
        .map(row => {
            const total = row.syn + row.sem + row.log + row.com;
            if (total === 0)
                return row;

            return {
                ...row,
                syn: (row.syn / total) * 100,
                sem: (row.sem / total) * 100,
                log: (row.log / total) * 100,
                com: (row.com / total) * 100,
                dateFormatted: new Date(row.date).toLocaleDateString(locale, {
                    month: 'short',
                    day: 'numeric'
                })
            };
        })
        .sort((a, b) => a.date.localeCompare(b.date));

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
                <strong style={{ color }}>{name}</strong><br />
                {CATEGORY_DESC[p.cat]}<br />
                {t('components.learningStats.errors.count_label', { count: value })}
            </div>
        );
    };

    const barTooltip = ({ payload }) => {
        if (!payload || !payload.length)
            return null;

        const { payload: row } = payload[0];

        return (
            <div style={{
                background: '#fff',
                border: '1px solid #ddd',
                padding: '12px 16px',
                borderRadius: '6px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                maxWidth: '600px'
            }}>
                <h4 style={{ fontWeight: 600 }}>{row.name}</h4>
                <span>{t(`errors.errors.${row.id}.description`)}</span>
                <br />
                <span>{t(`components.learningStats.errors.count_label`, { count: row.count })}</span>

                <hr style={{ opacity: 0.15 }} />

                <h5 className='mt-2 text-danger'>
                    {t('components.learningStats.errors.example_label')}
                </h5>
                <pre style={{
                    background: '#f8f9fa',
                    padding: '8px 10px',
                    borderLeft: '3px solid #dc3545',
                    borderRadius: '3px'
                }}>
                    {t(`errors.errors.${row.id}.example`)}
                </pre>

                <h5 className='mt-3 text-info'>
                    {t('components.learningStats.errors.explanation_label')}
                </h5>
                <i>{t(`errors.errors.${row.id}.explanation`)}</i>

                <h5 className='mt-3 text-success'>
                    {t('components.learningStats.errors.correction_label')}
                </h5>
                <pre style={{
                    background: '#f8f9fa',
                    padding: '8px 10px',
                    borderLeft: '3px solid #28a745',
                    borderRadius: '3px'
                }}>
                    {t(`errors.errors.${row.id}.correction`)}
                </pre>
            </div>
        );
    };

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {!hasErrors ? (
                <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                    {t(`components.learningStats.errors.empty.${role}`)}
                </p>
            ) : (
                <>
                    <Row className="mb-4">
                        {/* PIE */}
                        <Col>
                            <Card style={{ height: '100%' }}>
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
                        </Col>

                        {/* TIMELINE */}
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.errors.timeline_title.${role}`)}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.timeline_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <AreaChart data={timelineData} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                                            <CartesianGrid strokeDasharray="3 3" />

                                            <XAxis dataKey="dateFormatted" />
                                            <YAxis domain={[0, 100]} tickFormatter={(v) => `${v.toFixed(0)}%`} />

                                            <Tooltip
                                                formatter={(value, name) => {
                                                    const label = t(`errors.categories.${name}.name`);
                                                    return [`${value.toFixed(1)}%`, label];
                                                }}
                                                itemSorter={(entry) => {
                                                    // Desired order (top → bottom)
                                                    const ORDER = { com: 1, log: 2, sem: 3, syn: 4 };
                                                    return ORDER[entry.dataKey];
                                                }}
                                                wrapperStyle={{ zIndex: 1000 }}
                                            />

                                            <Legend formatter={(v) => t(`errors.categories.${v}.name`)} />

                                            <Area
                                                type="linear"
                                                dataKey="syn"
                                                stackId="1"
                                                stroke={CATEGORY_COLOR.syn}
                                                fill={CATEGORY_COLOR.syn}
                                                fillOpacity={0.35}
                                            />
                                            <Area
                                                type="linear"
                                                dataKey="sem"
                                                stackId="1"
                                                stroke={CATEGORY_COLOR.sem}
                                                fill={CATEGORY_COLOR.sem}
                                                fillOpacity={0.35}
                                            />
                                            <Area
                                                type="linear"
                                                dataKey="log"
                                                stackId="1"
                                                stroke={CATEGORY_COLOR.log}
                                                fill={CATEGORY_COLOR.log}
                                                fillOpacity={0.35}
                                            />
                                            <Area
                                                type="linear"
                                                dataKey="com"
                                                stackId="1"
                                                stroke={CATEGORY_COLOR.com}
                                                fill={CATEGORY_COLOR.com}
                                                fillOpacity={0.35}
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row className="mb-4">
                        {/* BAR */}
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t('components.learningStats.errors.common_title')}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.common_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    <ResponsiveContainer width="100%" height={40 * perErrorData.length}>
                                        <BarChart layout="vertical" data={perErrorData} margin={{ left: 40, right: 60 }}>
                                            <XAxis type="number" hide />
                                            <YAxis type="category" dataKey="name" width={200} />
                                            <Tooltip content={barTooltip} wrapperStyle={{ zIndex: 1000 }} />
                                            <Bar
                                                dataKey="count"
                                                isAnimationActive={false}
                                                shape={(props) => {
                                                    const barColor = CATEGORY_COLOR[props.payload.cat];
                                                    return (
                                                        <rect
                                                            x={props.x}
                                                            y={props.y}
                                                            width={props.width}
                                                            height={props.height}
                                                            fill={barColor}
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

                    </Row>
                </>
            )}
        </ObservedOnce>
    );
}

export default LearningStatsErrors;
