import { useTranslation } from 'react-i18next';

function ExerciseMask({ title, setTitle, request, setRequest, answer, setAnswer }) {
    const { t } = useTranslation();

    return (
        <>
            <div className="mb-3">
                <label className="form-label">{t('exercise_mask.title')}</label>
                <input
                    type="text"
                    className="form-control"
                    defaultValue={title}
                    onInput={(e) => setTitle(e.target.value)}
                />
            </div>

            <div className="mb-3">
                <label className="form-label">{t('exercise_mask.request')}</label>
                <textarea
                    className="form-control"
                    rows="3"
                    defaultValue={request}
                    onInput={(e) => setRequest(e.target.value)}
                />
            </div>

            <div className="mb-3">
                <label className="form-label">{t('exercise_mask.answer_optional')}</label>
                <textarea
                    className="form-control"
                    rows="3"
                    defaultValue={answer}
                    onInput={(e) => setAnswer(e.target.value)}
                />
            </div>
        </>
    );
}

export default ExerciseMask;
