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

    const queriesTotal = data?.queries || 0;
    const queriesUnique = data?.queries_d || 0;
    const queriesSuccess = data?.queries_success || 0;

    const querySuccessDataAll = [
        { name: t('components.learningStats.queries.success'), value: queriesSuccess },
        { name: t('components.learningStats.queries.fail'), value: queriesTotal - queriesSuccess },
    ];

    const queriesTotalSelect = data?.queries_select || 0;
    const queriesSuccessSelect = data?.queries_success_select || 0;
    const querySuccessDataSelect = [
        { name: t('components.learningStats.queries.success'), value: queriesSuccessSelect },
        { name: t('components.learningStats.queries.fail'), value: queriesTotalSelect - queriesSuccessSelect },
    ];

    const queryTypesData = data?.query_types.map(({ type, count, success }) => ({
        type,
        success,
        fail: count - success,
        total: count,
    }));

    const queryTypesTootlipFormatter = (value, name) => {
        const label = t(`components.learningStats.queries.${name}`) || name;
        return [value === 1 ? `${value} query` : `${value} queries`, label];
    };

    const role = isTeacher ? 'teacher' : 'student';

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {queriesTotal === 0 ? (
                <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                    {t(`components.learningStats.queries.empty.${role}`)}
                </p>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col xs={4}>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.queries.title.${role}`)}</Card.Title>
                                </Card.Header>
                                <Card.Body>
                                    <div>
                                        <strong>{t('components.learningStats.queries.stats.distinct')}:</strong> {queriesUnique}<br />
                                        <strong>{t('components.learningStats.queries.stats.total')}:</strong> {queriesTotal}
                                    </div>
                                    <div className="mt-2 text-muted" style={{ fontSize: '0.9rem' }}>
                                        {t('components.learningStats.queries.stats.note')}
                                    </div>
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t('components.learningStats.queries.success_title')}</Card.Title>
                                </Card.Header>
                                <Card.Body>
                                    <Row>
                                        <Col>
                                            <div className="text-center fw-bold" style={{ fontSize: '1.2rem' }}>
                                                {t('components.learningStats.queries.select_label')}
                                            </div>
                                            <ResponsiveContainer width="100%" height={100}>
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
                                                    <Tooltip formatter={(value, name) => [value === 1 ? `${value} query` : `${value} queries`, name]} />
                                                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                        {queriesTotalSelect === 0 ?
                                                            0 :
                                                            (queriesSuccessSelect / queriesTotalSelect * 100).toFixed(0)
                                                        }%
                                                    </text>
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </Col>
                                        <Col>
                                            <div className="text-center fw-bold" style={{ fontSize: '1.2rem' }}>
                                                {t('components.learningStats.queries.all_label')}
                                            </div>
                                            <ResponsiveContainer width="100%" height={100}>
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
                                                    <Tooltip formatter={(value, name) => [value === 1 ? `${value} query` : `${value} queries`, name]} />
                                                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                        {queriesTotal === 0 ?
                                                            0 :
                                                            (queriesSuccess / queriesTotal * 100).toFixed(0)
                                                        }%
                                                    </text>
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </Col>
                                    </Row>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row className="mb-4">
                        <Col>
                            <Card>
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
                                                <Tooltip formatter={queryTypesTootlipFormatter} />
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
