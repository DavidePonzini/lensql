import { useState } from "react";
import useAuth from "../../hooks/useAuth";
import ObservedOnce from "../../components/ObservedOnce";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

function Queries() {
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest('/api/users/stats/queries', 'GET');
        setData(response.data)
    }

    // Total queries box
    const queriesTotal = data?.queries || 0;
    const queriesUnique = data?.queries_d || 0;

    // Success rate box
    const queriesSuccess = data?.queries_success || 0;
    const querySuccessDataAll = [
        { name: 'Successful', value: queriesSuccess },
        { name: 'Failed', value: queriesTotal - queriesSuccess },
    ];

    const queriesTotalSelect = data?.queries_select || 0;
    const queriesSuccessSelect = data?.queries_success_select || 0;
    const querySuccessDataSelect = [
        { name: 'Successful', value: queriesSuccessSelect },
        { name: 'Failed', value: queriesTotalSelect - queriesSuccessSelect },
    ];

    // Query type breakdown box
    const queryTypesData = data?.query_types.map(({ type, count, success }) => ({
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

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            <Row className="mb-4">
                <Col xs={4}>
                    <Card style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>Your SQL Journey</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <div>
                                <strong>Distinct queries tried:</strong> {queriesUnique}
                                <br />
                                <strong>Total queries executed:</strong> {queriesTotal}
                            </div>
                            <div className="mt-2 text-muted" style={{ fontSize: '0.9rem' }}>
                                Every attempt helps — even retries are part of the learning curve.
                            </div>
                        </Card.Body>
                    </Card>
                </Col>

                <Col>
                    <Card style={{ height: '100%' }}>
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
                                                <Cell fill="#198754" /> {/* Green for success */}
                                                <Cell fill="#dc3545" /> {/* Red for failure */}
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
                                                <Cell fill="#198754" /> {/* Green for success */}
                                                <Cell fill="#dc3545" /> {/* Red for failure */}
                                            </Pie>
                                            <Tooltip formatter={(value, name) => [value === 1 ? `${value} query` : `${value} queries`, name]} />
                                            <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="bold">
                                                {queriesTotalSelect === 0 ?
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
                            <Card.Title>What kind of queries are you running?</Card.Title>
                            <Card.Subtitle className="text-muted">
                                Here's the mix of SQL commands you've used, and how they turned out.
                            </Card.Subtitle>
                        </Card.Header>
                        <Card.Body>
                            {queriesTotal === 0 ? (
                                <div className="text-center text-muted" style={{ fontSize: '1.2rem' }}>
                                    No queries run yet. Start exploring SQL!
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
        </ObservedOnce>
    );
}

export default Queries;