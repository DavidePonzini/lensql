import { useTranslation } from 'react-i18next';

function ExerciseMask({ title, setTitle, request, setRequest, solutions, setSolutions }) {
    const { t } = useTranslation();

    return (
        <>
            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.exercise_mask.title')}</label>
                <input
                    type="text"
                    className="form-control"
                    defaultValue={title}
                    onInput={(e) => setTitle(e.target.value)}
                    placeholder={t('pages.datasets.exercise_mask.title_placeholder')}
                />
            </div>

            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.exercise_mask.request')}</label>
                <textarea
                    className="form-control"
                    rows="3"
                    defaultValue={request}
                    onInput={(e) => setRequest(e.target.value)}
                    placeholder={t('pages.datasets.exercise_mask.request_placeholder')}
                />
            </div>

            <div className="mb-3">
                <label className="form-label">{t('pages.datasets.exercise_mask.answer_optional')}</label>

                {solutions.map((solution, idx) => (
                    <div>
                        <textarea
                            className="form-control"
                            rows="3"
                            key={idx}
                            defaultValue={solution}
                            onInput={(e) => {
                                const newSolutions = solutions.slice();
                                newSolutions[idx] = e.target.value;
                                setSolutions(newSolutions);
                            }}
                        />

                        <button
                            type="button"
                            className="btn btn-danger my-2"
                            key={`remove-${idx}`}
                            onClick={() => {
                                const newSolutions = solutions.slice();
                                newSolutions.splice(idx, 1);
                                setSolutions(newSolutions);
                            }}
                        >
                            {t('pages.datasets.exercise_mask.remove_answer')}
                        </button>
                    </div>
                ))}

                <div>
                    <button
                        type="button"
                        className="btn btn-success mt-2"
                        onClick={() => setSolutions([...solutions, ''])}
                    >
                        {t('pages.datasets.exercise_mask.add_answer')}
                    </button>
                </div>
            </div>
        </>
    );
}

export default ExerciseMask;
