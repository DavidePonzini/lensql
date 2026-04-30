import { useState } from "react";
import { useTranslation } from "react-i18next";

import useAuth from "../../hooks/useAuth";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ObservedOnce from "../ObservedOnce";

function LearningStatsQueries({ datasetId = null, exerciseId = null, isTeacher = false }) {
    const { apiRequest } = useAuth();
    const { t } = useTranslation();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/queries?dataset_id=${datasetId || ''}&exercise_id=${exerciseId || ''}&is_teacher=${isTeacher ? '1' : '0'}`,
            'GET');
        setData(response.data);
    }

    const queriesTotal = +(data?.queries) || 0;
    const queriesUnique = +(data?.queries_d) || 0;
    const queriesSuccess = +(data?.queries_success) || 0;

    const querySuccessDataAll = [
        { name: t('components.learningStats.queries.success'), value: queriesSuccess },
        { name: t('components.learningStats.queries.fail'), value: queriesTotal - queriesSuccess },
    ];

    const queriesTotalSelect = +(data?.queries_select) || 0;
    const queriesSuccessSelect = +(data?.queries_success_select) || 0;
    const querySuccessDataSelect = [
        { name: t('components.learningStats.queries.success'), value: queriesSuccessSelect },
        { name: t('components.learningStats.queries.fail'), value: queriesTotalSelect - queriesSuccessSelect },
    ];

    const queryTypesData = data?.query_types
        .map(({ type, count, success }) => ({
            type,
            success,
            fail: count - success,
            total: count,
        }))
        .sort((a, b) => b.total - a.total);

    const queryTypesTootlipFormatter = (value, name) => {
        const label = t(`components.learningStats.queries.${name}`) || name;
        return [value === 1 ? `${value} query` : `${value} queries`, label];
    };

    const role = isTeacher ? 'teacher' : 'student';

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {queriesTotal === 0 ? (
                <p className="text-muted learning-stats-empty" style={{ fontSize: '1.1rem' }}>
                    {t(`components.learningStats.queries.empty.${role}`)}
                </p>
            ) : (
                <>
                    <Row className="g-4 mb-4">
                        <Col lg={4}>
                            <Card className="learning-stats-panel">
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.queries.title.${role}`)}</Card.Title>
                                </Card.Header>
                                <Card.Body>
                                    <div className="learning-stats-kpis">
                                        <div className="learning-stats-kpi">
                                            <span className="learning-stats-kpi__label">{t('components.learningStats.queries.stats.distinct')}</span>
                                            <span className="learning-stats-kpi__value">{queriesUnique}</span>
                                        </div>
                                        <div className="learning-stats-kpi">
                                            <span className="learning-stats-kpi__label">{t('components.learningStats.queries.stats.total')}</span>
                                            <span className="learning-stats-kpi__value">{queriesTotal}</span>
                                        </div>
                                    </div>
                                    <div className="mt-2 text-muted" style={{ fontSize: '0.9rem' }}>
                                        {t('components.learningStats.queries.stats.note')}
                                    </div>
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col lg={8}>
                            <Card className="learning-stats-panel">
                                <Card.Header>
                                    <Card.Title>{t('components.learningStats.queries.success_title')}</Card.Title>
                                </Card.Header>
                                <Card.Body>
                                    <Row className="g-3">
                                        <Col>
                                            <div className="learning-stats-donut-card">
                                                <div className="learning-stats-donut-card__title">
                                                    {t('components.learningStats.queries.select_label')}
                                                </div>
                                                <ResponsiveContainer width="100%" height={110}>
                                                    <PieChart>
                                                        <Pie
                                                            data={querySuccessDataSelect}
                                                            dataKey="value"
                                                            innerRadius={25}
                                                            outerRadius={50}
                                                            startAngle={90}
                                                            endAngle={-270}
                                                        >
                                                            <Cell fill="#198754" />
                                                            <Cell fill="#dc3545" />
                                                        </Pie>
                                                        <Tooltip
                                                            formatter={(value, name) => [value === 1 ? `${value} query` : `${value} queries`, name]}
                                                            wrapperStyle={{ zIndex: 1000 }}
                                                        />
                                                        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                            {queriesTotalSelect === 0 ?
                                                                0 :
                                                                (queriesSuccessSelect / queriesTotalSelect * 100).toFixed(0)
                                                            }%
                                                        </text>
                                                    </PieChart>
                                                </ResponsiveContainer>
                                                <div className="learning-stats-donut-card__meta">
                                                    {queriesSuccessSelect}/{queriesTotalSelect}
                                                </div>
                                            </div>
                                        </Col>
                                        <Col>
                                            <div className="learning-stats-donut-card">
                                                <div className="learning-stats-donut-card__title">
                                                    {t('components.learningStats.queries.all_label')}
                                                </div>
                                                <ResponsiveContainer width="100%" height={110}>
                                                    <PieChart>
                                                        <Pie
                                                            data={querySuccessDataAll}
                                                            dataKey="value"
                                                            innerRadius={25}
                                                            outerRadius={50}
                                                            startAngle={90}
                                                            endAngle={-270}
                                                        >
                                                            <Cell fill="#198754" />
                                                            <Cell fill="#dc3545" />
                                                        </Pie>
                                                        <Tooltip
                                                            formatter={(value, name) => [value === 1 ? `${value} query` : `${value} queries`, name]}
                                                            wrapperStyle={{ zIndex: 1000 }}
                                                        />
                                                        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                            {queriesTotal === 0 ?
                                                                0 :
                                                                (queriesSuccess / queriesTotal * 100).toFixed(0)
                                                            }%
                                                        </text>
                                                    </PieChart>
                                                </ResponsiveContainer>
                                                <div className="learning-stats-donut-card__meta">
                                                    {queriesSuccess}/{queriesTotal}
                                                </div>
                                            </div>
                                        </Col>
                                    </Row>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row className="mb-4">
                        <Col>
                            <Card className="learning-stats-panel">
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.queries.chart_title.${role}`)}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.queries.chart_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {queriesTotal === 0 ? (
                                        <div className="text-center text-muted" style={{ fontSize: '1.2rem' }}>
                                            {t(`components.learningStats.queries.chart_empty.${role}`)}
                                        </div>
                                    ) : (
                                        <ResponsiveContainer width="100%" height={40 * queryTypesData?.length || 1}>
                                            <BarChart layout="vertical" data={queryTypesData} margin={{ left: 40, right: 60 }}>
                                                <XAxis type="number" hide />
                                                <YAxis dataKey="type" type="category" />
                                                <Tooltip
                                                    formatter={queryTypesTootlipFormatter}
                                                    wrapperStyle={{ zIndex: 1000 }}
                                                />
                                                <Bar dataKey="success" stackId="a" fill="#198754" />
                                                <Bar dataKey="fail" stackId="a" fill="#dc3545">
                                                    <LabelList dataKey="total" position="right" fill="#000" />
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    )}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}
        </ObservedOnce>
    );
}

export default LearningStatsQueries;
