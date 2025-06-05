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
    const messagesSuccess = profileData?.messages_success || 0;
    const messagesError = profileData?.messages_error || 0;

    const messagesFeedbackRate = profileData?.messages_feedback_perc || 0;
    // Feedback box
    const messagesFeedbackData = [
        { name: 'Given', value: messagesFeedbackRate },
        { name: 'Not Given', value: 1 - messagesFeedbackRate },
    ];

    return (
        <>
            <h1>
                {userInfo?.username}
            </h1>

            <hr />

            <h2>Let's look at your queries</h2>
            <Row className="mb-4">
                <Col xs={3}>
                    <Card bg="light" text="dark">
                        <Card.Header>
                            <Card.Title>Total Queries</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <OverlayTooltip
                                text="Total number of queries executed."
                            >
                                <Card.Text>
                                    All queries: {totalQueries}
                                    <br />
                                    Excluding repetitions: {uniqueQueries}
                                </Card.Text>
                            </OverlayTooltip>
                        </Card.Body>
                    </Card>
                </Col>
                <Col>
                    <Card bg="light" text="dark">
                        <Card.Header>
                            <Card.Title>Success Rate</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col>
                                    <OverlayTooltip
                                        text="Percentage of SELECT queries that were executed successfully."
                                    >
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
                                            </PieChart>
                                        </ResponsiveContainer>
                                        <div style={{
                                            textAlign: 'center',
                                            fontSize: '1.2rem',
                                            fontWeight: 'bold'
                                        }}>
                                            {(successRateSelect * 100).toFixed(2)}%
                                        </div>
                                    </OverlayTooltip>
                                </Col>
                                <Col>
                                    <OverlayTooltip
                                        text="Percentage of total queries that were executed successfully."
                                    >
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
                                            </PieChart>
                                        </ResponsiveContainer>
                                        <div style={{
                                            textAlign: 'center',
                                            fontSize: '1.2rem',
                                            fontWeight: 'bold'
                                        }}>
                                            {(successRateAll * 100).toFixed(2)}%
                                        </div>
                                    </OverlayTooltip>
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
                            <Card.Title>Query Type Breakdown</Card.Title>
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
            <h2>
                Help and Feedback
            </h2>
            <Row className="mb-4">
                <Col xs={3}>
                    <OverlayTooltip text="Number of times the help feature was used.">
                        <Card>
                            <Card.Header>
                                <Card.Title>Times help was used</Card.Title>
                            </Card.Header>
                            <Card.Body>
                                Total: {messagesTotal}<br />
                                SELECT queries: {messagesSelect}<br />
                                Help with results: {messagesSuccess}<br />
                                Help with errors: {messagesError}<br />
                            </Card.Body>
                        </Card>
                    </OverlayTooltip>
                </Col>
                <Col xs={3}>
                    <OverlayTooltip text="Number of times feedback was provided to the messages generated by LensQL.">
                        <Card>
                            <Card.Header>
                                <Card.Title>Feedback given</Card.Title>
                            </Card.Header>
                            <Card.Body>
                                <ResponsiveContainer width="100%" height={100}>
                                    <PieChart>
                                        <Pie
                                            data={messagesFeedbackData}
                                            dataKey="value"
                                            innerRadius={25}
                                            outerRadius={50}
                                            startAngle={90}
                                            endAngle={-270}
                                        >
                                            {messagesFeedbackData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                    </PieChart>
                                </ResponsiveContainer>
                                <div style={{
                                    textAlign: 'center',
                                    fontSize: '1.2rem',
                                    fontWeight: 'bold'
                                }}>
                                    {(messagesFeedbackRate * 100).toFixed(2)}%
                                </div>
                            </Card.Body>
                        </Card>
                    </OverlayTooltip>
                </Col>
            </Row>
        </>
    );
}

export default Profile;