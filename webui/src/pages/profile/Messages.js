import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

function Messages({ data }) {
    const COLORS = ['#198754', '#dc3545']; // Bootstrap green and red

    // Help box
    const messagesTotal = data?.messages || 0;
    const messagesSelect = data?.messages_select || 0;
    const messagesSuccessRate = data?.messages_success_rate || 0;
    const messagesErrorRate = data?.messages_error_rate || 0;

    const messagesBreakdownData = [
        { name: 'Understanding results', value: messagesSuccessRate },
        { name: 'Understanding errors', value: messagesErrorRate },
    ];

    const messagesFeedbackRate = data?.messages_feedback_rate || 0;

    // Feedback box
    const messagesFeedbackData = [
        { name: 'Feedback Given', value: messagesFeedbackRate },
        { name: 'Feedback Not Given', value: 1 - messagesFeedbackRate },
    ];

    return (
        <Row className="mb-4">
            <Col xs={6}>
                <Card style={{ height: '100%' }}>
                    <Card.Header>
                        <Card.Title>You asked, we explained</Card.Title>
                        <Card.Subtitle className="text-muted">
                            Got stuck or curious? Here's when you asked for explanations or guidance on your queries.
                        </Card.Subtitle>
                    </Card.Header>
                    <Card.Body>
                        <Row>
                            <Col>
                                <strong>When you asked for help:</strong>
                                <ul style={{ paddingLeft: '1.2em', marginBottom: '0.5rem' }}>
                                    <li>Total requests: {messagesTotal}</li>
                                    <li>On SELECT queries: {messagesSelect}</li>
                                </ul>
                            </Col>
                            <Col>
                                <strong>What you were looking for:</strong>
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
                                                <Cell fill="#0d6efd" /> {/* Blue for results */}
                                                <Cell fill="#ffc107" /> {/* Yellow for errors */}
                                            </Pie>
                                            <Tooltip formatter={(value, name) => [`${value * 100}%`, name]} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                                <div className="text-center text-muted" style={{ fontSize: '0.9rem' }}>
                                    <span style={{ color: '#0d6efd', fontWeight: 'bold' }}>Understanding results</span>:&nbsp;
                                    {(messagesSuccessRate * 100).toFixed(0)}%
                                    <br />
                                    <span style={{ color: '#ffc107', fontWeight: 'bold' }}>Understanding errors</span>:&nbsp;
                                    {(messagesErrorRate * 100).toFixed(0)}%
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
                        <Card.Title>
                            You rated the replies
                        </Card.Title>
                        <Card.Subtitle className="text-muted">
                            You gave a thumbs-up or down on the explanations — that helps us improve.
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
                                    {messagesFeedbackData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value, name) => [`${(value * 100)}%`, name]} />
                                <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                    {(messagesFeedbackRate * 100).toFixed(0)}%
                                </text>
                            </PieChart>
                        </ResponsiveContainer>
                    </Card.Body>
                </Card>
            </Col>
        </Row>
    );
}

export default Messages;