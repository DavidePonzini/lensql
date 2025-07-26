import { useState } from "react";
import useAuth from "../hooks/useAuth";
import ObservedOnce from "./ObservedOnce";
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import AlertUnderDevelopment from './AlertUnderDevelopment';

function Errors({ classId = null, exerciseId = null, isTeacher = false }) {
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/errors?class_id=${classId || ''}&exercise_id=${exerciseId || ''}`,
            'GET');
        setData(response.data)
    }

    if (data); // TODO: display data when available

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {true ? (
                <>
                    <AlertUnderDevelopment />
                    <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                        {isTeacher ?
                            "Your students haven't encountered any errors yet. When they do, we'll show you the types of errors they faced and how they changed over time."
                            : "You haven't encountered any errors yet. When you do, we'll show you the types of errors you faced and how they changed over time."
                        }
                    </p>
                </>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>What kind of issues came up?</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {isTeacher ?
                                            "Your students' errors fall into a few key patterns — here's the overview."
                                            : "Your errors fall into a few key patterns — here's the overview."
                                        }
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {isTeacher ?
                                        "Under development! This section will categorize your students' errors into Syntactic, Semantic, Logical Errors, and Complications."
                                        : "Under development! This section will categorize your errors into Syntactic, Semantic, Logical Errors, and Complications."
                                    }
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>Most common mistakes</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {isTeacher ?
                                            "Here are the most frequent error patterns detected in your students' queries."
                                            : "Here are the most frequent error patterns detected in your queries."
                                        }
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {isTeacher ?
                                        "Under development! This section will show the most common error patterns in your students' queries."
                                        : "Under development! This section will show the most common error patterns in your queries."
                                    }
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                    <Row className="mb-4">
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{isTeacher ? "How your students' errors changed over time" : "How your errors changed over time"}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {isTeacher ?
                                            "See whether your students are making fewer mistakes as they progress."
                                            : "See whether you're making fewer mistakes as you progress."
                                        }
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {isTeacher ?
                                        "Under development! This section will show a timeline of your students' errors, helping you track their progress."
                                        : "Under development! This section will show a timeline of your errors, helping you track your progress."
                                    }
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}
        </ObservedOnce >
    );
}

export default Errors;