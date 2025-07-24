import { useState } from 'react';
import { useAuth, RequestSizeError } from '../../hooks/useAuth';

import ButtonCategory from './ButtonCategory';
import ButtonAction from '../../components/ButtonAction';
import BubbleStatsChange from '../../components/BubbleStatsChange';

function ButtonsQuery({ exerciseId, isExecuting, setIsExecuting, sqlText, result, setResult }) {
    const { apiRequest, incrementStats } = useAuth();
    const [expChange, setExpChange] = useState(0);
    const [changeReason, setChangeReason] = useState('');

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
                
                if (done)
                    break;
                
                if (value) {
                    buffer += decoder.decode(value, { stream: true });

                    let lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep last partial line

                    for (let line of lines) {
                        if (line.trim() === '')
                            continue;

                        try {
                            const parsed = JSON.parse(line);

                            if (firstLine) {
                                incrementStats(0, parsed.exp_change || 0);
                                setExpChange(parsed.exp_change);
                                setChangeReason(parsed.exp_change_reason);
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
                alert(`Query too large. Please try to split it into smaller parts. You need to remove at least ${error.size - error.maxSize} characters.`);
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
                text="Query"
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
                    Execute
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
                    Clear output
                </ButtonAction>

                <BubbleStatsChange
                    expChange={expChange}
                    setExpChange={setExpChange}
                    changeReason={changeReason}
                    style={{ padding: '.4rem', marginBottom: '.25rem', verticalAlign: 'middle' }}
                />
            </div>
        </>
    );
}

export default ButtonsQuery;