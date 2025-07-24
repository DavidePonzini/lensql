import { useState } from 'react';
import useAuth from "../../hooks/useAuth";

import ButtonAction from "../../components/ButtonAction";
import ButtonShowDataset from "../../components/ButtonShowDataset";
import ButtonCategory from "./ButtonCategory";
import BubbleStatsChange from '../../components/BubbleStatsChange';

function ButtonsExercise({ exerciseId, classId, sqlText, isExecuting, setIsExecuting, setResult }) {
    const { apiRequest, incrementStats } = useAuth();
    const [expChange, setExpChange] = useState(0);
    const [coinsChange, setCoinsChange] = useState(0);
    const [changeReason, setChangeReason] = useState('');

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
            alert('Error when creating dataset. See console for details.\nIf the dataset is very large, you can try manually executing commands in smaller batches.');
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

        incrementStats(data[0].coins_change, data[0].exp_change);
        setChangeReason(data[0].change_reason);
        setExpChange(data[0].exp_change);
        setCoinsChange(data[0].coins_change);

        setResult(data);
    }

    return (
        <>
            <ButtonCategory
                text="Exercise"
                iconClassName='fas fa-tasks'
                className="text-info"
            />

            <div className="col">
                <ButtonShowDataset
                    variant="info"
                    className="me-1 mb-1"
                    buttonText="Dataset"
                    classId={classId}
                    disabled={isExecuting}
                    footerButtons={[
                        {
                            text: 'Create',
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
                    disabled={isExecuting || sqlText.trim().length === 0}
                >
                    Check Result
                </ButtonAction>

                <BubbleStatsChange
                    expChange={expChange}
                    setExpChange={setExpChange}
                    coinsChange={coinsChange}
                    setCoinsChange={setCoinsChange}
                    changeReason={changeReason}
                    style={{ padding: '.4rem', marginBottom: '.25rem', verticalAlign: 'middle' }}
                />
            </div>
        </>
    );

}

export default ButtonsExercise;