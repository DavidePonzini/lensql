import { useEffect, useState } from "react";
import useAuth from "../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import BootstrapTooltip from 'react-bootstrap/Tooltip';

function OverlayTooltip({ text, children }) {
    return (
        <OverlayTrigger
            placement="bottom"
            overlay={<BootstrapTooltip>{text}</BootstrapTooltip>}
        >
            <div>
                {children}
            </div>
        </OverlayTrigger>
    );
}

function Profile() {
    const { apiRequest, userInfo } = useAuth();
    const [profileData, setProfileData] = useState(null);

    useEffect(() => {
        // Example API call to fetch profile data
        async function fetchProfileData() {
            const response = await apiRequest('/api/users/learning-stats', 'GET');
            setProfileData(response.data)
        }

        fetchProfileData();
    }, [apiRequest]);   // eslint-disable-line react-hooks/exhaustive-deps

    // Total queries box
    const totalQueries = profileData?.queries || 0;
    const uniqueQueries = profileData?.queries_d || 0;

    // Success rate box
    const successRateAll = profileData?.success_rate || 0;
    const querySuccessDataAll = [
        { name: 'Success', value: successRateAll },
        { name: 'Fail', value: 1 - successRateAll },
    ];
    const successRateSelect = profileData?.success_rate_select || 0;
    const querySuccessDataSelect = [
        { name: 'Success', value: successRateSelect },
        { name: 'Fail', value: 1 - successRateSelect },
    ];
    const COLORS = ['#198754', '#dc3545']; // Bootstrap green and red

    // Query type breakdown box
    const queryTypesData = profileData?.query_types.map(({ type, count, success }) => ({
        type,
        success,
        fail: count - success,
        total: count,
    }));
    const queryTypesTootlipFormatter = (value, name) => {
        if (name === 'success') {
            if (value === 1)
                return [`${value} query`, 'Successful'];
            return [`${value} queries`, 'Successful'];
        } else if (name === 'fail') {
            if (value === 1)
                return [`${value} query`, 'Failed'];
            return [`${value} queries`, 'Failed'];
        }
        return [value, name];
    }

    // Help box
    const messagesTotal = profileData?.messages || 0;
    const messagesSelect = profileData?.messages_select || 0;
    const messagesSuccessRate = profileData?.messages_success_rate || 0;
    const messagesErrorRate = profileData?.messages_error_rate || 0;

    const messagesBreakdownData = [
        { name: 'Understanding results', value: messagesSuccessRate },
        { name: 'Understanding errors', value: messagesErrorRate },
    ];

    const messagesFeedbackRate = profileData?.messages_feedback_rate || 0;
    
    // Feedback box
    const messagesFeedbackData = [
        { name: 'Feedback Given', value: messagesFeedbackRate },
        { name: 'Feedback Not Given', value: 1 - messagesFeedbackRate },
    ];

    return (
        <>
            <h1>Welcome back, {userInfo?.username || 'user'}!</h1>
            <p>Here's a quick look at your SQL progress — keep going strong!</p>
            <hr />

            <h2>Let's look at your queries</h2>
            <Row className="mb-4">
                <Col xs={4}>
                    <Card bg="light" text="dark" style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>Your SQL Journey</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <div>
                                <strong>Total queries run:</strong> {totalQueries}
                                <br />
                                <strong>Distinct queries tried:</strong> {uniqueQueries}
                            </div>
                            <div className="mt-2 text-muted" style={{ fontSize: '0.9rem' }}>
                                Every attempt helps — even retries are part of the learning curve.
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
                <Col>
                    <Card bg="light" text="dark" style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>How often things worked</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col>
                                    <div style={{
                                        textAlign: 'center',
                                        fontSize: '1.2rem',
                                        fontWeight: 'bold'
                                    }}>
                                        SELECT Queries
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
                                                {querySuccessDataSelect.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(value, name) => [`${value * 100}%`, name]} />
                                            <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                {(successRateSelect * 100).toFixed(0)}%
                                            </text>
                                        </PieChart>
                                    </ResponsiveContainer>
                                </Col>
                                <Col>
                                    <div style={{
                                        textAlign: 'center',
                                        fontSize: '1.2rem',
                                        fontWeight: 'bold'
                                    }}>
                                        All Queries
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
                                                {querySuccessDataAll.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(value, name) => [`${value * 100}%`, name]} />
                                            <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                {(successRateAll * 100).toFixed(0)}%
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
                            <Card.Title>What kind of queries are you running?</Card.Title>
                            <Card.Subtitle className="text-muted">
                                Here's the mix of SQL commands you've used, and how they turned out.
                            </Card.Subtitle>
                        </Card.Header>
                        <Card.Body>
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
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <hr />
            <h2>Turning Questions Into Progress</h2>
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
                <Col></Col>
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
                                    <Tooltip formatter={(value, name) => [`${value} times`, name]} />
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
    );
}

export default Profile;