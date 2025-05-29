import { useEffect, useState } from "react";
import useAuth from "../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import BootstrapTooltip from 'react-bootstrap/Tooltip';

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

    const processedData = profileData?.query_types.map(({ type, count, success }) => ({
        type,
        success,
        fail: count - success,
        total: count,
    }));

    const tootlipFormatter = (value, name) => {
        if (name === 'success') {
            if (value === 1)
                return [`${value} query`, 'No Syntax Errors'];
            return [`${value} queries`, 'No Syntax Errors'];
        } else if (name === 'fail') {
            if (value === 1)
                return [`${value} query`, 'Syntax Errors'];
            return [`${value} queries`, 'Syntax Errors'];
        }
        return [value, name];
    }

    const successRate = profileData ? ((profileData.queries_success / profileData.queries) * 100).toFixed(2) : 0;
    const totalQueries = profileData ? profileData.queries : 0;
    const uniqueQueries = profileData ? profileData.queries_d : 0;

    function renderTooltip(msg) {
        return (
            <BootstrapTooltip>{msg}</BootstrapTooltip>
        );
    }

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
                        <Col md={4}>
                            <OverlayTrigger
                                placement="bottom"
                                overlay={renderTooltip('Total number of queries executed, including repeated ones.')}
                            >
                                <Card bg="light" text="dark">
                                    <Card.Body>
                                        <Card.Title>Total Queries</Card.Title>
                                        <Card.Text>{totalQueries}</Card.Text>
                                    </Card.Body>
                                </Card>
                            </OverlayTrigger>
                        </Col>
                        <Col md={4}>
                            <OverlayTrigger
                                placement="bottom"
                                overlay={renderTooltip('Number of distinct queries executed, regardless of how many times they were repeated.')}
                            >
                                <Card bg="light" text="dark">
                                    <Card.Body>
                                        <Card.Title>Unique Queries</Card.Title>
                                        <Card.Text>{uniqueQueries}</Card.Text>
                                    </Card.Body>
                                </Card>
                            </OverlayTrigger>
                        </Col>
                        <Col md={4}>
                            <OverlayTrigger
                                placement="bottom"
                                overlay={renderTooltip('Percentage of total queries that were executed successfully.')}
                            >
                                <Card bg="light" text="dark">
                                    <Card.Body>
                                        <Card.Title>Success Rate</Card.Title>
                                        <Card.Text>{successRate}%</Card.Text>
                                    </Card.Body>
                                </Card>
                            </OverlayTrigger>
                        </Col>
                    </Row>
                    
                    <Row>
                        <Col>
                            <Card>
                                <Card.Body>
                                    <Card.Title>Query Type Breakdown</Card.Title>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart layout="vertical" data={processedData} margin={{ left: 40, right: 60 }}>
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="type" type="category" />
                                            <Tooltip formatter={tootlipFormatter} />
                                            <Bar dataKey="success" stackId="a" fill="#198754">
                                                <LabelList dataKey="total" position="right" fill="#000" />
                                            </Bar>
                                            <Bar dataKey="fail" stackId="a" fill="#dc3545">
                                                <LabelList dataKey="total" position="right" fill="#000" />
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}
        </div>
    );
}

export default Profile;