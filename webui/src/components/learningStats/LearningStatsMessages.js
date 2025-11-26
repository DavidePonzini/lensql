import { useState } from "react";
import { useTranslation } from "react-i18next";

import useAuth from "../../hooks/useAuth";

import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ObservedOnce from "../ObservedOnce";

function LearningStatsMessages({ datasetId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/messages?dataset_id=${datasetId || ''}&exercise_id=${exerciseId || ''}&is_teacher=${isTeacher ? '1' : '0'}`,
            'GET');
        setData(response.data);
    }

    const messagesTotal = data?.messages || 0;
    const messagesSelect = data?.messages_select || 0;
    const messagesSuccess = data?.messages_success || 0;
    const messagesError = messagesTotal - messagesSuccess;
    const messagesSuccessRate = messagesTotal > 0 ? messagesSuccess / messagesTotal : 0;
    const messagesErrorRate = messagesTotal > 0 ? messagesError / messagesTotal : 0;

    const messagesBreakdownData = [
        { name: t('components.learningStats.messages.understanding_results'), value: messagesSuccess },
        { name: t('components.learningStats.messages.understanding_errors'), value: messagesError },
    ];

    const messagesFeedback = data?.messages_feedback || 0;
    const messagesFeedbackRate = messagesTotal > 0 ? messagesFeedback / messagesTotal : 0;

    const messagesFeedbackData = [
        { name: t('components.learningStats.messages.feedback_given'), value: messagesFeedback },
        { name: t('components.learningStats.messages.feedback_not_given'), value: messagesTotal - messagesFeedback },
    ];

    const role = isTeacher ? 'teacher' : 'student';

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {messagesTotal === 0 ? (
                <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                    {t(`components.learningStats.messages.empty.${role}`)}
                </p>
            ) : (
                <Row className="mb-4">
                    <Col xs={6}>
                        <Card style={{ height: '100%' }}>
                            <Card.Header>
                                <Card.Title>{t(`components.learningStats.messages.title_help.${role}`)}</Card.Title>
                                <Card.Subtitle className="text-muted">
                                    {t(`components.learningStats.messages.subtitle_help.${role}`)}
                                </Card.Subtitle>
                            </Card.Header>
                            <Card.Body>
                                <Row>
                                    <Col>
                                        <strong>{t(`components.learningStats.messages.list_title.${role}`)}</strong>
                                        <ul style={{ paddingLeft: '1.2em', marginBottom: '0.5rem' }}>
                                            <li>{t('components.learningStats.messages.list_labels.total')}: {messagesTotal}</li>
                                            <li>{t('components.learningStats.messages.list_labels.select')}: {messagesSelect}</li>
                                        </ul>
                                    </Col>
                                    <Col>
                                        <strong>{t(`components.learningStats.messages.chart_title.${role}`)}</strong>
                                        <div style={{ width: '100%', height: '90px', overflow: 'hidden' }}>
                                            <ResponsiveContainer width="100%" height={140}>
                                                <PieChart>
                                                    <Pie
                                                        data={messagesBreakdownData}
                                                        dataKey="value"
                                                        innerRadius={40}
                                                        outerRadius={60}
                                                        startAngle={180}
                                                        endAngle={0}
                                                        paddingAngle={2}
                                                        cx="50%"
                                                        cy="50%"
                                                    >
                                                        <Cell fill="#0d6efd" />
                                                        <Cell fill="#ffc107" />
                                                    </Pie>
                                                    <Tooltip formatter={(value, name) => [value === 1 ? `${value} time` : `${value} times`, name]} />
                                                </PieChart>
                                            </ResponsiveContainer>
                                        </div>
                                        <div className="text-center text-muted" style={{ fontSize: '0.9rem' }}>
                                            <span style={{ color: '#0d6efd', fontWeight: 'bold' }}>
                                                {t('components.learningStats.messages.understanding_results')}
                                            </span>: {(messagesSuccessRate * 100).toFixed(0)}%
                                            <br />
                                            <span style={{ color: '#ffc107', fontWeight: 'bold' }}>
                                                {t('components.learningStats.messages.understanding_errors')}
                                            </span>: {(messagesErrorRate * 100).toFixed(0)}%
                                        </div>
                                    </Col>
                                </Row>
                            </Card.Body>
                        </Card>
                    </Col>

                    <Col style={{ textAlign: 'center', placeContent: 'center' }}>
                        <i className="far fa-handshake text-secondary" style={{ fontSize: '5rem' }}></i>
                    </Col>

                    <Col xs={4}>
                        <Card style={{ height: '100%' }}>
                            <Card.Header>
                                <Card.Title>{t(`components.learningStats.messages.title_feedback.${role}`)}</Card.Title>
                                <Card.Subtitle className="text-muted">
                                    {t(`components.learningStats.messages.subtitle_feedback.${role}`)}
                                </Card.Subtitle>
                            </Card.Header>
                            <Card.Body>
                                <ResponsiveContainer width="100%">
                                    <PieChart>
                                        <Pie
                                            data={messagesFeedbackData}
                                            dataKey="value"
                                            innerRadius={35}
                                            outerRadius={70}
                                            startAngle={90}
                                            endAngle={-270}
                                        >
                                            <Cell fill='#20c997' />
                                            <Cell fill='#f8f9fa' />
                                        </Pie>
                                        <Tooltip formatter={(value, name) => [value === 1 ? `${value} time` : `${value} times`, name]} />
                                        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                            {(messagesFeedbackRate * 100).toFixed(0)}%
                                        </text>
                                    </PieChart>
                                </ResponsiveContainer>
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
            )}
        </ObservedOnce>
    );
}

export default LearningStatsMessages;
