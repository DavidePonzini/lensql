import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useAuth, RequestSizeError } from '../../hooks/useAuth';

import ButtonAction from '../../components/buttons/ButtonAction';
import BubbleStatsChange from '../../components/notifications/BubbleStatsChange';
import { setBadges } from '../../components/notifications/BadgeNotifier';

import ButtonCategory from './ButtonCategory';

function ButtonsQuery({ exerciseId, isExecuting, setIsExecuting, sqlText, result, setResult }) {
    const { t } = useTranslation();
    const { apiRequest } = useAuth();
    const [rewards, setRewards] = useState([]);

    async function handleExecute() {
        if (!sqlText.trim()) return;

        setIsExecuting(true);
        setResult([]);

        try {
            const stream = await apiRequest('/api/queries/run', 'POST', {
                'query': sqlText,
                'exercise_id': exerciseId,
            }, { stream: true });

            const reader = stream.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let firstLine = true;

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

                            if (firstLine) {
                                const rewards = parsed.rewards || [];
                                const badges = parsed.badges || [];

                                setRewards(rewards);
                                setBadges(badges);

                                firstLine = false;
                            } else {
                                setResult(prev => [...prev, parsed]);
                            }
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
            if (error instanceof RequestSizeError) {
                alert(t('pages.exercises.buttons.query.query_too_large', {
                    excess: error.size - error.maxSize
                }));
            } else {
                alert(error);
                console.error('Streaming error:', error);
            }
        } finally {
            setIsExecuting(false);
        }
    }

    function handleClearOutput() {
        setResult([]);
    }

    return (
        <>
            <ButtonCategory
                text={t('pages.exercises.buttons.category.query')}
                iconClassName='fas fa-align-left'
                className="text-primary"
            />

            <div className="col">
                <ButtonAction
                    variant="primary"
                    className="me-1 mb-1"
                    onClick={handleExecute}
                    disabled={isExecuting || sqlText.trim().length === 0}
                >
                    {t('pages.exercises.buttons.query.execute')}
                    {isExecuting && (
                        <span className="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true"></span>
                    )}
                </ButtonAction>

                <ButtonAction
                    variant="outline-primary"
                    className="me-1 mb-1"
                    onClick={handleClearOutput}
                    disabled={isExecuting || result.length === 0}
                >
                    {t('pages.exercises.buttons.query.clear_output')}
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

export default ButtonsQuery;
