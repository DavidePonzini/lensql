import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import useAuth from "../../hooks/useAuth";
import useGamificationData from '../../hooks/useGamificationData';

import ButtonAction from "../../components/buttons/ButtonAction";
import ButtonShowDataset from "../../components/buttons/ButtonShowDataset";
import { setBadges } from '../../components/notifications/BadgeNotifier';
import BubbleStatsChange from '../../components/notifications/BubbleStatsChange';

import ButtonCategory from "./ButtonCategory";

function ButtonsExercise({ exerciseId, classId, sqlText, isExecuting, setIsExecuting, setResult, attempts: initialAttempts, hasSolution }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const { Coins } = useGamificationData();

    const [rewards, setRewards] = useState([]);
    const [attempts, setAttempts] = useState(initialAttempts);

    async function handleCreateDataset() {
        setIsExecuting(true);
        setResult([]);

        try {
            const stream = await apiRequest('/api/exercises/init-dataset', 'POST', {
                'exercise_id': exerciseId,
            }, { stream: true });

            const reader = stream.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                if (value) {
                    buffer += decoder.decode(value, { stream: true });

                    let lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep last partial line

                    for (let line of lines) {
                        if (line.trim() === '') continue;
                        try {
                            const parsed = JSON.parse(line);
                            setResult(prev => [...prev, parsed]);
                        } catch (e) {
                            console.error('Failed to parse line:', line);
                        }
                    }
                }
            }

            if (buffer.trim() !== '') {
                try {
                    const parsed = JSON.parse(buffer);
                    setResult(prev => [...prev, parsed]);
                } catch (e) {
                    console.error('Failed to parse last buffer:', buffer);
                }
            }

        } catch (error) {
            alert(t('pages.exercises.buttons.exercise.dataset_error'));
            console.error('Streaming error:', error);
        } finally {
            setIsExecuting(false);
        }
    }

    async function handleCheckResult() {
        setIsExecuting(true);

        const data = await apiRequest('/api/queries/check-solution', 'POST', {
            'query': sqlText,
            'exercise_id': exerciseId,
        });

        setIsExecuting(false);

        setAttempts(data[0].attempts);
        setRewards(data[0].rewards || []);
        setBadges(data[0].badges || []);

        setResult(data);
    }

    return (
        <>
            <ButtonCategory
                text={t('pages.exercises.buttons.category.exercise')}
                iconClassName='fas fa-tasks'
                className="text-info"
            />

            <div className="col">
                <ButtonShowDataset
                    variant="info"
                    className="me-1 mb-1"
                    buttonText={t('pages.exercises.buttons.exercise.dataset')}
                    classId={classId}
                    disabled={isExecuting}
                    footerButtons={[
                        {
                            text: t('pages.exercises.buttons.exercise.create'),
                            variant: 'primary',
                            onClick: handleCreateDataset,
                            autoClose: true,
                            disabled: isExecuting,
                        },
                    ]}
                />

                <ButtonAction
                    variant="warning"
                    className="me-1 mb-1"
                    onClick={handleCheckResult}
                    disabled={isExecuting || sqlText.trim().length === 0 || !hasSolution}
                    cost={hasSolution ? Coins.checkSolutionCost(attempts) : null}
                >
                    {t('pages.exercises.buttons.exercise.check_result')}
                    <span className="text-muted ms-2">
                        (
                        {hasSolution ?
                            t(
                                attempts === 1
                                    ? 'pages.exercises.buttons.exercise.attempt_singular'
                                    : 'pages.exercises.buttons.exercise.attempt_plural',
                                { count: attempts }
                            )
                            : t('pages.exercises.buttons.exercise.no_solution')}
                        )
                    </span>
                </ButtonAction>

                <BubbleStatsChange
                    rewards={rewards}
                    setRewards={setRewards}
                    style={{ padding: '.4rem', marginBottom: '.25rem', verticalAlign: 'middle' }}
                />
            </div>
        </>
    );
}

export default ButtonsExercise;
