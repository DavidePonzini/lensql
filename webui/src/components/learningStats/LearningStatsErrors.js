import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from "../../hooks/useAuth";

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, LabelList } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import ObservedOnce from "../ObservedOnce";

function LearningStatsErrors({ classId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/errors?class_id=${classId || ''}&exercise_id=${exerciseId || ''}`,
            'GET'
        );
        setData(response.data);  
    }

    const role = isTeacher ? 'teacher' : 'student';

    // ---------------- CATEGORY MAPPING (your rules) ----------------
    function categoryOf(id) {
        if (id < 39) return 'syn';
        if (id < 52) return 'sem';
        if (id < 82) return 'log';
        return 'com';
    }

    // ---------------- CATEGORY COLORS ----------------
    const CATEGORY_COLOR = {
        syn: '#d9534f',   // reddish
        sem: '#fd7e14',   // orange
        log: '#0d6efd',   // blue
        com: '#198754',   // green
    };

    // ---------------- FULL ERROR NAME + DESCRIPTION MAPPING ----------------
    // You will fill translations later in i18n files.
    const ERROR_NAME = {
        // example: 1: t('errors.1.name'),
        // fill all IDs here
    };

    const ERROR_DESC = {
        // example: 1: t('errors.1.desc'),
        // fill all IDs here
    };

    // ---------------- CATEGORY DESCRIPTION (shown in pie hover) ----------------
    const CATEGORY_DESC = {
        syn: t('errors.categories.syn.description'),
        sem: t('errors.categories.sem.description'),
        log: t('errors.categories.log.description'),
        com: t('errors.categories.com.description'),
    };

    // ---------------- DATA PREPARATION ----------------
    const errorList = data || [];

    const categoryCounts = { syn: 0, sem: 0, log: 0, com: 0 };
    for (const { error_id, count } of errorList) {
        categoryCounts[categoryOf(error_id)] += count;
    }

    const categoryData = [
        { cat: 'syn', name: t('errors.categories.syn.name'), value: categoryCounts.syn },
        { cat: 'sem', name: t('errors.categories.sem.name'), value: categoryCounts.sem },
        { cat: 'log', name: t('errors.categories.log.name'), value: categoryCounts.log },
        { cat: 'com', name: t('errors.categories.com.name'), value: categoryCounts.com },
    ];

    // per-error chart data
    const perErrorData = [...errorList]
        .sort((a, b) => b.count - a.count)
        .map(({ error_id, count }) => ({
            id: error_id,
            count,
            name: t(`errors.errors.${error_id}.name`),
            cat: categoryOf(error_id),
        }));

    const hasErrors = errorList.length > 0;

    // ---------------- TOOLTIP FORMATTERS ----------------
    const pieTooltip = ({ payload }) => {
        if (!payload || !payload.length) return null;
        const { name, value, payload: p } = payload[0];
        return (
            <div style={{ background: '#fff', border: '1px solid #ccc', padding: '5px 10px' }}>
                <strong>{name}</strong><br />
                {CATEGORY_DESC[p.cat]}<br />
                {value} errors
            </div>
        );
    };

    const barTooltip = ({ payload }) => {
        if (!payload || !payload.length) return null;
        const { payload: row } = payload[0];
        return (
            <div style={{ background: '#fff', border: '1px solid #ccc', padding: '5px 10px' }}>
                <strong>{row.name}</strong><br />
                {t(`errors.errors.${row.id}.description`)}<br />
                {row.count} errors
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
                    {/* CATEGORY PIE + COMMON ERRORS BAR CHART */}
                    <Row className="mb-4">
                        {/* PIE CHART */}
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
                                            <Tooltip content={pieTooltip} />
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

                        {/* COMMON ERROR BAR CHART */}
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
                                        <BarChart layout="vertical" data={perErrorData} margin={{ left: 60, right: 60 }}>
                                            <XAxis type="number" hide />
                                            <YAxis type="category" dataKey="name" />
                                            <Tooltip content={barTooltip} />
                                            <Bar 
                                                dataKey="count" 
                                                fill="#000" 
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

                    {/* TIMELINE PLACEHOLDER */}
                    <Row className="mb-4">
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.errors.timeline_title.${role}`)}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.timeline_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {t(`components.learningStats.errors.timeline_body.${role}`)}
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
