import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

function Queries({ data }) {
    const COLORS = ['#198754', '#dc3545']; // Bootstrap green and red

    // Total queries box
    const totalQueries = data?.queries || 0;
    const uniqueQueries = data?.queries_d || 0;

    // Success rate box
    const successRateAll = data?.success_rate || 0;
    const querySuccessDataAll = [
        { name: 'Success', value: successRateAll },
        { name: 'Fail', value: 1 - successRateAll },
    ];
    const successRateSelect = data?.success_rate_select || 0;
    const querySuccessDataSelect = [
        { name: 'Success', value: successRateSelect },
        { name: 'Fail', value: 1 - successRateSelect },
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
        <>
            <Row className="mb-4">
                <Col xs={4}>
                    <Card style={{ height: '100%' }}>
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

            {totalQueries > 0 && (
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
            )}
        </>
    );
}

export default Queries;