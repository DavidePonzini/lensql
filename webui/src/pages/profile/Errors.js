import { useEffect, useState } from "react";
import useAuth from "../../hooks/useAuth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, PieChart, Pie, Cell } from 'recharts';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

function Errors({ data }) {
    return (
        <>
            <Row className="mb-4">
                <Col>
                    <Card style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>What kind of issues came up?</Card.Title>
                            <Card.Subtitle className="text-muted">
                                Your errors fall into a few key patterns — here's the overview.
                            </Card.Subtitle>
                        </Card.Header>
                        <Card.Body>
                            Under development! This section will categorize your errors into Syntactic, Semantic, Logical Errors, and Complications.
                        </Card.Body>
                    </Card>
                </Col>

                <Col>
                    <Card style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>Most common mistakes</Card.Title>
                            <Card.Subtitle className="text-muted">
                                Here are the most frequent error patterns detected in your queries.
                            </Card.Subtitle>
                        </Card.Header>
                        <Card.Body>
                            Under development! This section will show the most common error patterns in your queries.
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
            <Row className="mb-4">
                <Col>
                    <Card style={{ height: '100%' }}>
                        <Card.Header>
                            <Card.Title>How your errors changed over time</Card.Title>
                            <Card.Subtitle className="text-muted">
                                See whether you're making fewer mistakes as you progress.
                            </Card.Subtitle>
                        </Card.Header>
                        <Card.Body>
                            Under development! This section will show a timeline of your errors, helping you track your progress.
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </>
    );
}

export default Errors;