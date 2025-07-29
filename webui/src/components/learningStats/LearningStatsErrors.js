import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from "../../hooks/useAuth";

import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ObservedOnce from "../ObservedOnce";
import AlertUnderDevelopment from '../AlertUnderDevelopment';

function LearningStatsErrors({ classId = null, exerciseId = null, isTeacher = false }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [data, setData] = useState(null);

    async function fetchData() {
        const response = await apiRequest(
            `/api/users/stats/errors?class_id=${classId || ''}&exercise_id=${exerciseId || ''}`,
            'GET'
        );
        setData(response.data);
    }

    if (data); // TODO: display data when available

    const role = isTeacher ? 'teacher' : 'student';

    return (
        <ObservedOnce onFirstVisible={fetchData}>
            {true ? (
                <>
                    <AlertUnderDevelopment />
                    <p className="text-muted" style={{ fontSize: '1.2rem' }}>
                        {t(`components.learningStats.errors.empty.${role}`)}
                    </p>
                </>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t('components.learningStats.errors.kind_title')}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.kind_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {t(`components.learningStats.errors.kind_body.${role}`)}
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t('components.learningStats.errors.common_title')}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.common_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {t(`components.learningStats.errors.common_body.${role}`)}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row className="mb-4">
                        <Col>
                            <Card style={{ height: '100%' }}>
                                <Card.Header>
                                    <Card.Title>{t(`components.learningStats.errors.timeline_title.${role}`)}</Card.Title>
                                    <Card.Subtitle className="text-muted">
                                        {t(`components.learningStats.errors.timeline_subtitle.${role}`)}
                                    </Card.Subtitle>
                                </Card.Header>
                                <Card.Body>
                                    {t(`components.learningStats.errors.timeline_body.${role}`)}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}
        </ObservedOnce>
    );
}

export default LearningStatsErrors;
