import { useState } from "react";
import useAuth from "../hooks/useAuth";
import ObservedOnce from "./ObservedOnce";
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

function Messages({ classId = null, exerciseId = null, isTeacher = false }) {
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/messages?class_id=${classId || ''}&exercise_id=${exerciseId || ''}`,
            'GET');
        setData(response.data)
    }

    // Help box
    const messagesTotal = data?.messages || 0;
    const messagesSelect = data?.messages_select || 0;
    const messagesSuccess = data?.messages_success || 0;
    const messagesError = messagesTotal - messagesSuccess;

    const messagesSuccessRate = messagesTotal > 0 ? messagesSuccess / messagesTotal : 0;
    const messagesErrorRate = messagesTotal > 0 ? messagesError / messagesTotal : 0;

    const messagesBreakdownData = [
        { name: 'Understanding results', value: messagesSuccess },
        { name: 'Understanding errors', value: messagesError },
    ];

    const messagesFeedback = data?.messages_feedback || 0;
    const messagesFeedbackRate = messagesTotal > 0 ? messagesFeedback / messagesTotal : 0;

    // Feedback box
    const messagesFeedbackData = [
        { name: 'Feedback Given', value: messagesFeedback },
        { name: 'Feedback Not Given', value: messagesTotal - messagesFeedback },
    ];

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {messagesTotal === 0 ? (
                <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                    {isTeacher ?
                        "Your students haven't asked for help yet. When they do, we'll show you how often they asked for explanations and how well they understood the replies."
                        : "You haven't asked for help yet. When you do, we'll show you how often you asked for explanations and how well you understood the replies."
                    }
                </p>
            ) : (
                <>

                    <Row className="mb-4">
                        <Col xs={6}>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{isTeacher ? "Your students asked, we explained" : "You asked, we explained"}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {isTeacher ?
                                            "Got stuck or curious? Here's when your students asked for explanations or guidance on their queries."
                                            : "Got stuck or curious? Here's when you asked for explanations or guidance on your queries."
                                        }
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    <Row>
                                        <Col>
                                            <strong>{isTeacher ? "When your students asked for help:" : "When you asked for help:"}</strong>
                                            <ul style={{ paddingLeft: '1.2em', marginBottom: '0.5rem' }}>
                                                <li>Total requests: {messagesTotal}</li>
                                                <li>On SELECT queries: {messagesSelect}</li>
                                            </ul>
                                        </Col>
                                        <Col>
                                            <strong>{isTeacher ? "What your students were looking for:" : "What you were looking for:"}</strong>
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
                                                        <Tooltip formatter={(value, name) => [value === 1 ? `${value} time` : `${value} times`, name]} />
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
                                        {isTeacher ? "Your students rated the replies" : "You rated the replies"}
                                    </Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {isTeacher ?
                                            "Your students gave a thumbs-up or down on the explanations — that helps us improve."
                                            : "You gave a thumbs-up or down on the explanations — that helps us improve."
                                        }
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
                                                <Cell fill='#20c997' /> {/* Teal for feedback given */}
                                                <Cell fill='#f8f9fa' /> {/* Light gray for feedback not given */}
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
                </>
            )}
        </ObservedOnce>
    );
}

export default Messages;