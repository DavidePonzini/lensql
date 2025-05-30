import { useEffect, useState } from "react";
import useAuth from "../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import BootstrapTooltip from 'react-bootstrap/Tooltip';

function StatCard({ title, children, value, tooltip }) {
    return (
        <Col>
            <OverlayTrigger
                placement="bottom"
                overlay={<BootstrapTooltip>{tooltip}</BootstrapTooltip>}
            >
                <Card bg="light" text="dark">
                    <Card.Body>
                        <Card.Title>{title}</Card.Title>
                        {children}
                        {value && <Card.Text>{value}</Card.Text>}
                    </Card.Body>
                </Card>
            </OverlayTrigger>
        </Col>
    );
}

function Profile() {
    const { apiRequest, userInfo } = useAuth();
    const [profileData, setProfileData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Example API call to fetch profile data
        async function fetchProfileData() {
            const response = await apiRequest('/api/users/learning-stats', 'GET');
            setProfileData(response.data)

            setLoading(false);
        }

        fetchProfileData();
    }, [apiRequest]);   // eslint-disable-line react-hooks/exhaustive-deps

    const queryTypesData = profileData?.query_types.map(({ type, count, success }) => ({
        type,
        success,
        fail: count - success,
        total: count,
    }));

    const tootlipFormatter = (value, name) => {
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

    const totalQueries = profileData?.queries || 0;
    const uniqueQueries = profileData?.queries_d || 0;

    const querySuccessData = [
        { name: 'Success', value: profileData?.queries_success || 0 },
        { name: 'Fail', value: (profileData?.queries || 0) - (profileData?.queries_success || 0) },
    ];
    const COLORS = ['#198754', '#dc3545']; // Bootstrap green and red
    const successRate = totalQueries > 0 ? ((profileData.queries_success / totalQueries) * 100).toFixed(0) : 0;

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>
                {userInfo?.username}
            </h1>
            <hr />

            {profileData && (
                <>
                    <Row className="mb-4">
                        <StatCard
                            title="Total Queries"
                            tooltip="Total number of queries executed, including repeated ones."
                            value={totalQueries}
                        />
                        <StatCard
                            title="Unique Queries"
                            tooltip="Number of distinct queries executed, regardless of how many times they were repeated."
                            value={uniqueQueries}
                        />
                        <StatCard
                            title="Success Rate"
                            tooltip="Percentage of total queries that were executed successfully."
                        >
                            <ResponsiveContainer width="100%" height={100}>
                                <PieChart>
                                    <Pie
                                        data={querySuccessData}
                                        dataKey="value"
                                        innerRadius={25}
                                        outerRadius={50}
                                        startAngle={90}
                                        endAngle={-270}
                                    >
                                        {querySuccessData.map((entry, index) => (
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
                                {successRate}%
                            </div>
                        </StatCard>
                    </Row>

                    <Row className="mb-4">
                        <Col>
                            <Card>
                                <Card.Body>
                                    <Card.Title>Query Type Breakdown</Card.Title>
                                    <ResponsiveContainer width="100%" height={40 * profileData.query_types.length}>
                                        <BarChart layout="vertical" data={queryTypesData} margin={{ left: 40, right: 60 }}>
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="type" type="category" />
                                            <Tooltip formatter={tootlipFormatter} />
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

                    <Row className="mb-4">
                        <StatCard
                            title="Times help was used"
                            tooltip="Number of times the help feature was used."
                            value='0'
                        />
                        <StatCard
                            title="Feedback given"
                            tooltip="Number of times feedback was provided to the messages generated by LensQL."
                            value='0%'
                        />
                    </Row>
                </>
            )}
        </div>
    );
}

export default Profile;